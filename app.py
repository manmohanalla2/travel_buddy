import os
import time

from datetime import timedelta


from celery import Celery
from flask import Flask, render_template, flash, request, redirect, session, abort, url_for
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

from db import LoginPage

# App config. 
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = os.urandom(12)

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

class CommonTravellers(Form):
    name_a = TextField('Find users with City:', validators=[validators.required()])

class Login(Form):
    username = TextField('Username:', validators=[validators.required()])
    password = TextField('Password', validators=[validators.required()])

class Register(Form):
    f_name = TextField('First Name:', validators=[validators.required()])
    l_name = TextField('Last Name:', validators=[validators.required()])
    email = TextField('Email:', validators=[validators.required()])
    password = TextField('Password:', validators=[validators.required()])
    city = TextField('City Visiting:', validators=[validators.required()])
    p_number = TextField('Phone Number:', validators=[validators.required()])


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

@app.route('/login', methods=['POST'])
def do_login():
    form = Login(request.form)
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        #validating Form
        if form.validate():
            # calling class
            valid = LoginPage()
            data = valid.sign_in(username,password)
            if data == True:
                session['logged_in'] = True
                session['username'] = username
            else:
                flash('Username or password does not match our database')
        else:
            flash('Error: All the form fields are required. ')      
    return common_followers()

@app.route("/logout")
def logout():
    session.clear()
    form = Login(request.form)
    return render_template('login.html', form=form)

@app.errorhandler(404)
def page_not_found(e):
    form = Login(request.form)
    return render_template('login.html', form=form), 404

@app.errorhandler(405)
def method_not_allowed(e):
    form = Login(request.form)
    return render_template('login.html', form=form), 405

@app.route("/", methods=['GET', 'POST']) 
def common_followers():
    if not session.get('logged_in'):
        form = Login(request.form)
        return render_template('login.html', form=form)
    else:
        form = CommonTravellers(request.form)     
        return render_template('index.html', form=form)

@app.route("/common_travellers", methods=['GET', 'POST'])        
def common_followers_output():
    if not session.get('logged_in'):
        form = Login(request.form)
        return render_template('login.html', form=form)
    else:
        form = CommonTravellers(request.form) 
        if request.method == 'POST':
            name_a=request.form['name_a']
            #validating Form
            if form.validate():
                # calling class
                db = LoginPage()
                username = session.get("username")
                #printing the travellers
                data = db.get_common_travellers(name_a, username)
                if data:
                    for i in data:
                        flash("Travellers \n Name: {} \n Phone Number: {}".format(i['f_name'], i['p_number']))
                else:
                    flash('No Users Found.')  
    return render_template('index.html', form=form)

# @app.route("/add_city", methods=['GET', 'POST'])

@app.route("/signup", methods=['GET', 'POST'])
def sign_up():

    form = Register(request.form)

    if request.method == 'POST':
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        p_number = request.form['p_number']
        city = request.form['city']
        print city, p_number
        if form.validate():
            # calling class
            db = LoginPage()
            # signup
            data = celery_sign_up.delay(f_name, l_name, username, email, password, city, p_number)
            # data = db.sign_up(f_name, l_name, username, email, password, city, p_number)
            # if data == True:
            #     flash('Successfully Signed Up')
            # else:
            #     flash(data)
            flash("please wait to get an email")
        else:
            flash('Error: All the form fields are required. ')
    return render_template('register.html', form=form)

@celery_app.task
def celery_sign_up(f_name, l_name, username, email, password, city, p_number):
    # calling class
    db = LoginPage()
    # signup
    data = db.sign_up(f_name, l_name, username, email, password, city, p_number)
    return data

if __name__ == '__main__':
    app.run(host='0.0.0.0')

