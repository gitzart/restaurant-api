from mongoengine import *
from passlib.hash import pbkdf2_sha256

db_name = 'restaurantdb'
db = connect(db_name)


class User(Document):
    name = StringField(required=True, unique=True)
    password_hash = StringField()
    meta = {
        'indexes': ['name', '$name']
    }

    def __repr__(self):
        return '<User: {}>'.format(self.name)

    def hash_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    def verify(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)


class Restaurant(Document):
    name = StringField(required=True)
    address = StringField()
    photo = StringField()

    def __repr__(self):
        return '<Restaurant: {}>'.format(self.id)
