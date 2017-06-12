from mongoengine import *
from passlib.hash import pbkdf2_sha256
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)


db_name = 'restaurantdb'
db = connect(db_name)
SECRET_KEY = 'fhzcal8p#9rn@ei6q@-%92pus(qz)h$1t$+9igk#w7$34d9_!v'


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

    def generate_token(self, expiration=30):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': str(self.id)})

    @staticmethod
    def verify_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        return data['id']


class Restaurant(Document):
    name = StringField(required=True)
    address = StringField()
    photo = StringField()

    def __repr__(self):
        return '<Restaurant: {}>'.format(self.id)
