from flask import Flask, g, request, redirect, url_for,send_from_directory,  render_template
from flask.ext.login import LoginManager , request, redirect, url_for
from flask.ext.mongoengine import MongoEngine
from werkzeug import secure_filename, SharedDataMiddleware
from log_analyzer import LogParser, LogAnalyzer
import os


UPLOAD_FOLDER = '/var/tmp/'
#ALLOWED_EXTENSIONS = set(['txt','csv'])

app = Flask(
        __name__,\
        static_url_path='',\
        static_folder = './angular/app/',\
        template_folder='./angular/app/')

# overriding default jinja template tags, to avoid conflicts with angularjs
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'

#create the db connection, username and password only set if it exists
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['MONGODB_USERNAME'] = os.environ.get('MONGO_DB_USERNAME')
app.config['MONGODB_PASSWORD'] = os.environ.get('MONGO_DB_PASSWORD')
app.config['MONGODB_DB'] = 'test'
db = MongoEngine(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#set up login manager
login_manager = LoginManager()
login_manager.setup_app(app)

#set url to redirect to for login
login_manager.login_view = '/signin'

from User import User

#setting up user_loader callback, for Flask login
@login_manager.user_loader
def load_user(userid):
    return User.objects.get(id = userid)

#setting debug here to make sure that some routes are loaded only in debug mode
app.debug = True

import views

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file :
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            lp=LogParser()
            lp.load_apache_log_file_into_DB(UPLOAD_FOLDER + filename,filename)
            la=LogAnalyzer()
            la.count_hits(filename)
            return '''Upload successful'''
    return render_template('upload.html')
