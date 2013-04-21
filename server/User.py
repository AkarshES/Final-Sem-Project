from server import db
from flask.ext.login import UserMixin

class User(db.Document, UserMixin):
    '''
    A class that represents users who will use this system
    '''
    name = db.StringField(required = True, unique = True)
    password_hash = db.StringField(max_length = 160)
