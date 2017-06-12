# import json

from flask import Flask, request, jsonify, abort, g
from flask_httpauth import HTTPBasicAuth
# from mongoengine.base import BaseDocument
# from bson import json_util

from findARestaurant import findARestaurant
from models import User, Restaurant

app = Flask(__name__)
auth = HTTPBasicAuth()


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
