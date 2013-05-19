from flask import Flask, g, request, redirect, url_for,send_from_directory,  render_template
from flask.ext.login import LoginManager , request, redirect, url_for
from flask.ext.mongoengine import MongoEngine, DoesNotExist
import os
from log_analyzer import LogParser


UPLOAD_FOLDER = '/var/tmp/'
#ALLOWED_EXTENSIONS = set(['txt','csv'])

app = Flask(
        __name__\
        , static_url_path='/static'\
        , static_folder = '../angular/app/'\
        , template_folder='../angular/app/jinja-templates'\
    )

# overriding default jinja template tags, to avoid conflicts with angularjs
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

#allow debugging heroku code
if os.environ.get('DEBUG'):
    app.config['DEBUG'] = True

#create the db connection, username and password only set if it exists
if os.environ.get('ENV', 'dev') == 'pro':
    app.config['MONGODB_HOST'] = os.environ.get('MONGOLAB_URI')
    app.config['MONGODB_DB'] = 'final'
else:
    app.config['MONGODB_USERNAME'] = os.environ.get('MONGO_DB_USERNAME')
    app.config['MONGODB_PASSWORD'] = os.environ.get('MONGO_DB_PASSWORD')
    app.config['MONGODB_DB'] = 'test'

db = MongoEngine(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#set up login manager
login_manager = LoginManager()
login_manager.init_app(app)

#set url to redirect to for login
login_manager.login_view = 'signin'

from User import User

#setting up user_loader callback, for Flask login
@login_manager.user_loader
def load_user(userid):
    try:
        return User.objects.get(id = userid)
    except DoesNotExist:
        return None

import views
