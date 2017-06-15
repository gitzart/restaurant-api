# import json
import time

from functools import wraps

from flask import Flask, request, jsonify, abort, g
from flask_httpauth import HTTPBasicAuth
from redis import StrictRedis
# from mongoengine.base import BaseDocument
# from bson import json_util

from findARestaurant import findARestaurant
from models import User, Restaurant

app = Flask(__name__)
auth = HTTPBasicAuth()
redis = StrictRedis()


class RateLimit:
    expiration_window = 10

    def __init__(self, key_prefix, limit, per, send_x_headers):
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        p = redis.pipeline()
        p.incr(self.key)
        p.expireat(self.key, self.reset + self.expiration_window)
        self.current = min(p.execute()[0], limit)

    remaining = property(lambda x: x.limit - x.current)
    over_limit = property(lambda x: x.current >= x.limit)


def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)


def on_over_limit(limit):
    return jsonify(data='You hit the rate limit', error='429'), 429


def rate_limit(limit, per=60, send_x_headers=True, over_limit=on_over_limit,
               scope_func=lambda: request.remote_addr,
               key_func=lambda: request.endpoint):
    def decorator(f):
        @wraps(f)
        def rate_limited(*args, **kwargs):
            key = 'rate-limit/{}/{}/'.format(key_func(), scope_func())
            rlimit = RateLimit(key, limit, per, send_x_headers)
            g._view_rate_limit = rlimit
            if over_limit is not None and rlimit.over_limit:
                return over_limit(rlimit)
            return f(*args, **kwargs)
        return rate_limited
    return decorator


@app.after_request
def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response


@auth.verify_password
def verify_pw(username_or_token, password):
    user_id = User.verify_token(username_or_token)
    if user_id:
        user = User.objects(id=user_id).first()
    else:
        user = User.objects(name=username_or_token).first()
        if not user or not user.verify(password):
            return False
    g.user = user
    return True


@app.route('/token')
@auth.login_required
def get_token():
    return jsonify(token=g.user.generate_token().decode())


@app.route('/users', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    if username is None or password is None:
        abort(400)
    if User.objects(name=username):
        abort(400)
    user = User(name=username)
    user.hash_password(password)
    user.save()
    return jsonify(User=user.name), 201


# class MongoEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, BaseDocument):
#             data = o.to_mongo()
#             o_id = data.pop('_id', None)
#             if o_id:
#                 data['id'] = str(o_id)
#             data.pop('_cls', None)
#             return data
#         return super().default(o)


@app.route('/', methods=['GET', 'POST'])
@app.route('/restaurants', methods=['GET', 'POST'])
@auth.login_required
@rate_limit(limit=300)
def restaurants():
    if request.method == 'GET':
        # restaurants = Restaurant.objects  # (id='59368a24756a44140214809e')
        return Restaurant.objects.to_json()
        # r = Restaurant._collection.find(Restaurant.objects()._query)
        # return json.dumps(restaurants, cls=MongoEncoder)
    elif request.method == 'POST':
        name, address, photo = findARestaurant(
            request.form.get('mealType'),
            request.form.get('location')
        )
        restaurant = Restaurant(
            name=name,
            address=address,
            photo=photo
        ).save()
        return restaurant.to_json()


@app.route('/restaurants/<id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
@rate_limit(limit=300)
def restaurants_with_id(id):
    if request.method == 'GET':
        return Restaurant.objects(id=id).to_json()
    elif request.method == 'PUT':
        restaurant = Restaurant.objects(id=id)
        restaurant.update(
            name=request.form.get('name'),
            photo=request.form.get('image'),
            address=request.form.get('location')
        )
        return restaurant.to_json()
    elif request.method == 'DELETE':
        Restaurant.objects(id=id).delete()
        return '200'


if __name__ == '__main__':
    app.run(debug=True)
