from flask import render_template, send_from_directory
from server import app

def signin():
    pass

def signout():
    pass

def index():
    """ The main page """
    return render_template('index.html')

def sample_data_returner(filename):
    """ Helper function to return sample data in debug mode """
    return send_from_directory('./angular/sample_data', filename)

app.add_url_rule('/', view_func=index)

if app.debug is True:
    app.add_url_rule('/sample_data/<path:filename>', view_func=sample_data_returner)
