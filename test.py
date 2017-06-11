import base64
import unittest

from flask_testing import TestCase

from app import app
from models import db, db_name


base_url = 'http://localhost:5000'
user_url = base_url + '/users'
restaurant_url = base_url + '/restaurants'
specific_restaurant_url = base_url + '/restaurants/'
credentials = 'Basic ' + base64.b64encode(b'nut:althebest').decode('ascii')
invalid_credentials = 'Basic ' + base64.b64encode(b'nut:althe').decode('ascii')
user_data = [
    dict(username='nut', password='althebest'),
    dict(username='krack', password='krackthenut'),
]
restaurant_data = [
    dict(location='Buenos Aires Argentina', mealType='Sushi'),
    dict(location='Denver Colorado', mealType='Soup'),
    dict(location='Prague Czech Republic', mealType='Crepes'),
    dict(location='Shanghai China', mealType='Sandwiches'),
    dict(location='Nairobi Kenya', mealType='Pizza'),
]
upgrade_restaurant_data = [
    dict(
        name="Trader Joe's",
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
    def test_user_can_create_account(self):
        for i in user_data:
            resp = self.client.post(user_url, data=i)
            print(resp.json)
            self.assertEqual(resp.status_code, 201)

    def test_user_can_add_restaurants(self):
        self.client.post(user_url, data=user_data[0])
        for i in restaurant_data:
            resp = self.client.post(restaurant_url, data=i,
                                    headers={'Authorization': credentials})
            print(resp.json)
            self.assertEqual(resp.status_code, 200)

    def test_user_can_read_restaurants(self):
        self.client.post(user_url, data=user_data[0])
        for i in restaurant_data[:2]:
            self.client.post(restaurant_url, data=i,
                             headers={'Authorization': credentials})
        resp = self.client.get(restaurant_url,
                               headers={'Authorization': credentials})
        print('-------', resp.json)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json), 2)

    def test_user_cant_read_restaurants_with_invalid_credentials(self):
        self.client.post(user_url, data=user_data[0])
        for i in restaurant_data[:2]:
            self.client.post(restaurant_url, data=i,
                             headers={'Authorization': credentials})
        resp = self.client.get(restaurant_url,
                               headers={'Authorization': invalid_credentials})
        self.assertEqual(resp.status_code, 401)

    def test_user_can_read_specific_restaurant(self):
        self.client.post(user_url, data=user_data[0])
        for i in restaurant_data[2:4]:
            resp = self.client.post(restaurant_url, data=i,
                                    headers={'Authorization': credentials})
            id = resp.json['_id']['$oid']
            print('-------', id)
        resp = self.client.get(specific_restaurant_url + id,
                               headers={'Authorization': credentials})
        print('-------', resp.json[0]['_id']['$oid'])
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json[0]['_id']['$oid'], id)

    def test_user_can_update_specific_restaurant(self):
        self.client.post(user_url, data=user_data[0])
        for i in restaurant_data[3:]:
            resp = self.client.post(restaurant_url, data=i,
                                    headers={'Authorization': credentials})
            id = resp.json['_id']['$oid']
            name = resp.json['name']
            print('-------', name)
        resp = self.client.put(
            specific_restaurant_url + id,
            data=upgrade_restaurant_data[0],
            headers={'Authorization': credentials}
        )
        print('-------', resp.json[0]['name'])
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(name == resp.json[0]['name'])

    def test_user_can_delete_specific_restaurant(self):
        self.client.post(user_url, data=user_data[0])
        for i in restaurant_data[1:3]:
            resp = self.client.post(restaurant_url, data=i,
                                    headers={'Authorization': credentials})
            id = resp.json['_id']['$oid']
        resp = self.client.delete(specific_restaurant_url + id,
                                  headers={'Authorization': credentials})
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(restaurant_url,
                               headers={'Authorization': credentials})
        print('------', len(restaurant_data[1:3]) - 1)
        self.assertEqual(len(resp.json), len(restaurant_data[1:3]) - 1)


if __name__ == '__main__':
    unittest.main()
