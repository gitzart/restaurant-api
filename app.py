# import json

from flask import Flask, request
# from mongoengine.base import BaseDocument
# from bson import json_util
from findARestaurant import findARestaurant
from models import Restaurant

app = Flask(__name__)


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
