from flask import request, render_template, redirect, url_for, flash, jsonify, send_from_directory
from flask.ext.mongoengine import DoesNotExist, ValidationError
from flask.ext.login import login_required, logout_user, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug import secure_filename
from server import app, db
from User import User
from Logsets_metadata import ApacheAccessLogsetMetadata, LogsetMetadata
from log_analyzer import LogAnalyzer, LogParser
import os
from datetime import datetime

def signin():
    """all logic to check whether a user exists and log him in"""
    error = None
    if request.method == 'POST':
        try:
            user = User.objects.get(name = request.form['name'])
            isCorrectPassword = check_password_hash(user.password_hash, request.form['password'])
            if isCorrectPassword and login_user(user) is True:
                flash("Logged in successfully.")
                return redirect(request.args.get("next") or url_for("index"))
            else:
                error = 'Failed to log in'
        except DoesNotExist:
            error = 'User with this name does not exist'
    return render_template('signin.html', error=error)

@login_required
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
                name = request.form['name']\
                , password_hash = generate_password_hash(request.form['password'])\
                )
        try:
            #wait for result and force inserts
            new_user.save(safe = True, force_insert=True)
            flash('successfully signed up')
            return redirect(url_for('signin'))
        except db.NotUniqueError:
            error = 'User with this username already exists'
        except ValidationError as e:
            if e.errors.get('name'):
                error = 'Invalid name'
            else:
                app.logger.error('An unknown validation error occured while trying to sign up a user')
                error = 'An internal server error stopped you from signing up'
    return render_template('signup.html', error=error)

@login_required
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

@login_required
def index():
    """ The main page """
    return render_template('index.html')

def sample_data_returner(filename):
    """ Helper function to return sample data in debug mode """
    return send_from_directory('./angular/sample_data', filename)

@login_required
def log_data_retriever(logset_name):

    arguments = {}
    arguments['collection'] = current_user.name + '_' + logset_name
    if request.args.get('from'):
        arguments['from_date'] = datetime.fromtimestamp(int( request.args.get('from') ))
    if request.args.get('to'):
        arguments['to_date'] = datetime.fromtimestamp(int( request.args.get('to') ))
    la = LogAnalyzer(**arguments)

    # old arguments not required, so reassigned
    arguments = {}
    operation = request.args.get('op', 'view')
    if operation == 'count':
        df = la.load_apache_logs_into_DataFrame()
        # if field is absent bad request(400) is returned
        field = request.args['field']
        data = la.group_by(df, field)
        data = la.count(data, field)
        data = la.to_dict(data, key_label = field, value_label = operation)
    elif operation == 'view':
        if request.args.get('page'):
            arguments['page_number'] = int(request.args.get('page'))
        data = la.get_log_data(**arguments)
    else:
        app.logger.warning('Invalid operation ' + operation + ' requested')
        #return a response indicating that the request could not be processed
        return jsonify('Invalid operation received'), 422

    return jsonify(data)

@login_required
def upload_logset():
    new_logset = ApacheAccessLogsetMetadata(\
                name = request.form['name']\
                , creator_name = current_user.name\
                , users_with_access = [current_user.name]\
            )
    uploaded_file = request.files['file']
    if uploaded_file:
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        lp = LogParser()
        file_location = app.config['UPLOAD_FOLDER'] + filename
        collection_name = current_user.name + '_' + request.form['name']
        if lp.load_apache_log_file_into_DB(file_location, collection_name) is False:
            return jsonify(dict(status = 'Error', message='The data was not stored'))
        try:
            new_logset.save()
            return jsonify(dict(status = 'Success', message = 'Upload successful'))
        except db.NotUniqueError:
            return jsonify(dict(status = 'Error', message = 'Logset by this name already exists'))
    else:
        return jsonify(dict(status = 'Error', message = 'No file provided'))

@login_required
def get_logsets():
    names = []
    for logset in LogsetMetadata.objects(creator_name = current_user.name):
        la = LogAnalyzer(collection = current_user.name + '_' + logset.name)
        names.append(dict(\
                name = logset.name\
                , fields = logset.fields\
                , date_range = la.get_log_date_range()\
                ))
    return jsonify(dict(data = names))

@login_required
def delete_logset(logset_name):
    # remove logset from metadata
    LogsetMetadata.objects.get(\
        name = logset_name\
        , creator_name = current_user.name\
        ).delete()
    la = LogAnalyzer(collection = current_user.name + '_' + logset_name)
    la.collection.drop()
    return jsonify(dict(status = 'Success', message = 'logset deleted'))
