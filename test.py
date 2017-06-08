import unittest

from flask_testing import TestCase
from mongoengine import *

from app import app
from models import db, db_name, Restaurant


BASE_URL = 'http://localhost:5000'

restaurant_data = [
    dict(
        location='Buenos Aires Argentina',
        mealType='Sushi'
    ),
    dict(
        location='Denver Colorado',
        mealType='Soup'
    ),
    dict(
        location='Prague Czech Republic',
        mealType='Crepes'
    ),
    dict(
        location='Shanghai China',
        mealType='Sandwiches'
    ),
    dict(
        location='Nairobi Kenya',
        mealType='Pizza'
    ),
]

upgrade_restaurant_data = [
    dict(
        name='Udacity',
        address='2465, Latham Street, Mountain View, CA',
        image='https://media.glassdoor.com/l/70/82/fc/e8/students-first.jpg'
    ),
]


class BaseTest(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def setUp(self):
        # self.db = connect('test_restaurant_db')
        pass

    def tearDown(self):
        try:
            db.drop_database(db_name)
        except Exception as err:
            print('-------', err.args)


class RestaurantTests(BaseTest):
    def test_user_can_add_restaurants(self):
        for i in restaurant_data:
            resp = self.client.post('{}/restaurants'.format(BASE_URL), data=i)
            print(resp.json)
            self.assertEqual(resp.status_code, 200)

    def test_user_can_read_restaurants(self):
        for i in restaurant_data[:2]:
            self.client.post('{}/'.format(BASE_URL), data=i)
        resp = self.client.get('{}/restaurants'.format(BASE_URL))
        print('-------', resp.json)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json), 2)

    def test_user_can_read_specific_restaurant(self):
        for i in restaurant_data[2:4]:
            resp = self.client.post('{}/'.format(BASE_URL), data=i)
            id = resp.json['_id']['$oid']
            print('-------', id)
        resp = self.client.get('{}/restaurants/{}'.format(BASE_URL, id))
        print('------', resp.json[0]['_id']['$oid'])
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json[0]['_id']['$oid'], id)

    def test_user_can_update_specific_restaurant(self):
        for i in restaurant_data[3:]:
            resp = self.client.post('{}/'.format(BASE_URL), data=i)
            id = resp.json['_id']['$oid']
            name = resp.json['name']
            print('-------', name)
        resp = self.client.put(
            '{}/restaurants/{}'.format(BASE_URL, id),
            data=upgrade_restaurant_data[0]
        )
        print('------', resp.json[0]['name'])
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(name == resp.json[0]['name'])

    def test_user_can_delete_specific_restaurant(self):
        for i in restaurant_data[1:3]:
            resp = self.client.post('{}/'.format(BASE_URL), data=i)
            id = resp.json['_id']['$oid']
        resp = self.client.delete('{}/restaurants/{}'.format(BASE_URL, id))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('{}/'.format(BASE_URL))
        print('------', len(restaurant_data[1:3]) - 1)
        self.assertEqual(len(resp.json), len(restaurant_data[1:3]) - 1)


if __name__ == '__main__':
    unittest.main()
