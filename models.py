from mongoengine import *

db_name = 'restaurantdb'
db = connect(db_name)


class Restaurant(Document):
    name = StringField(required=True)
    address = StringField()
    photo = StringField()

    def __repr__(self):
        return '<Restaurant: {}>'.format(self.id)
