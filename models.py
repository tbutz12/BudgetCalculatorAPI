from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import DeclarativeMeta
from json import JSONEncoder
import json
#models
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    username = db.Column(db.String(80), unique = True)
    password = db.Column(db.String(20), unique = False)
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
            return '<User %r>' % self.username

class Categories(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    categoryName = db.Column(db.String(80), unique = False)
    amount = db.Column(db.Float, unique = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, id, categoryName, amount):
        self.id = id
        self.categoryName = categoryName
        self.amount = amount

class PurchaseList(db.Model):
    __tablename__ = 'purchase_list'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), unique = False)
    categoryName = db.Column(db.String(80), unique = False)
    amount = db.Column(db.Float, unique = False)
    purchaseDate = db.Column(db.String(80), unique = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    def __init__(self, name, categoryName, amount, purchaseDate):
        self.name = name
        self.categoryName = categoryName
        self.amount = amount
        self.purchaseDate = purchaseDate

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)

    
