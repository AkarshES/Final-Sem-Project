from flask import Response, request, render_template, redirect, url_for, flash, jsonify, send_from_directory
from flask.ext.mongoengine import DoesNotExist, ValidationError
from flask.ext.login import login_required, logout_user, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from server import app, db
from User import User
from log_analyzer import LogAnalyzer

def signin():
    """all logic to check whether a user exists and log him in"""
    error = None
    if request.method == 'POST':
        try:
            user = User.objects.get(email = request.form['email'])
            if check_password_hash(user.password_hash, request.form['password']) is True:
                login_user(user)
                return redirect(url_for('index'))
            else:
                error = 'Incorrect Password'
        except DoesNotExist:
            error = 'User with this email id does not exist'
    return render_template('signin.html', error=error)

def signout():
    '''all logic to correctly logout a user'''
    logout_user()
    flash('logged out')
    return redirect(url_for('signin'))

def signup():
    '''all logic to correctly signup a user'''
    error = None
    if request.method == 'POST':
        new_user = User(\
                email = request.form['email']\
                , name = request.form['name']\
                , password_hash = generate_password_hash(request.form['password'])\
                )
        try:
            #wait for result and force inserts
            new_user.save(safe = True, force_insert=True)
            flash('successfully signed up')
            return redirect(url_for('signin'))
        except db.NotUniqueError:
            error = 'User with this email id already exists'
        except ValidationError as e:
            if e.errors.get('email'):
                error = 'Invalid email'
            elif e.errors.get('name'):
                error = 'Invalid name'
            else:
                app.logger.error('An unknown validation error occured while trying to sign up a user')
                error = 'An internal server error stopped you from signing up'
    return render_template('signup.html', error=error)

def changePassword():
    '''Logic to change the password of the logged in user'''
    error = None
    if request.method == 'POST':
        if check_password_hash(current_user.password_hash, request.form['Old_Password']) is False:
            error = 'incorrect original password'
        elif(request.form['New_Password'] != request.form['Confirm_Password']):
            error = 'New password and confirm password do not match'
        else:
            current_user.password_hash = generate_password_hash(request.form['New_Password'])
            try:
                current_user.save(safe = True)
                flash('Your password has been changed')
                return redirect(url_for('index'))
            except db.OperationError:
                error = 'Failed to save new password, try again later'
    return render_template('changePassword.html', error = error)

def index():
    """ The main page """
    return render_template('index.html')

def sample_data_returner(filename):
    """ Helper function to return sample data in debug mode """
    return send_from_directory('./angular/sample_data', filename)

def log_data_retriever(collection_name):
    la = LogAnalyzer()
    data = la.get_log_data(collection_name)
    if data is False:
        return jsonify(dict(status = 'Error', message='The collection does not exist'))
    return data

def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file :
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            lp=LogParser()
            lp.load_apache_log_file_into_DB(UPLOAD_FOLDER + filename, filename)
            return 'Upload successful, to view the logs at <a href="http://127.0.0.1:5000/#/logviewer/'+filename+'" />Click here</a>'
    return render_template('upload.html')

app.add_url_rule('/signin', view_func=signin, methods=['GET', 'POST'])
app.add_url_rule('/signout', view_func=signout)
app.add_url_rule('/signup', view_func=signup, methods=['GET', 'POST'])
app.add_url_rule('/changePassword', view_func=changePassword, methods=['GET', 'POST'])

app.add_url_rule('/', view_func=index)
app.add_url_rule('/upload', view_func=upload_file, methods=['GET', 'POST'])
app.add_url_rule('/data/<string:collection_name>', view_func=log_data_retriever)

if app.debug is True:
    app.add_url_rule('/sample_data/<path:filename>', view_func=sample_data_returner)
