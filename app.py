import os
from flask import Flask, render_template, flash, redirect, request, url_for, session
from flask_bcrypt import Bcrypt
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from functools import wraps

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config["MONGO_DBNAME"] = "the_worlds_cookbook"
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template("index.html", recipes=mongo.db.recipes.find())
    
# Register Form Class (WTForms)
class RegistrationForm(Form):
    firstname = StringField('First Name', [validators.Length(min=4, max=15)])
    lastname = StringField('Last Name', [validators.Length(min=4, max=15)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
 
# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        users = mongo.db.users
        
        if users.find_one({'email': form.email.data }):
            flash('Email already registered, please login.')
            return redirect(url_for('login'))
        else:
            user = {
            'firstname': form.firstname.data,
            'lastname': form.lastname.data,
            'email': form.email.data,
            'password': bcrypt.generate_password_hash(form.password.data)}
            
            users.insert_one(user)
            
            flash('You are now registered and can login', 'success')
            return redirect(url_for('login'))
        
    return render_template('register.html', form=form)
    
    
# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['user_email']
        password_candidate = request.form['user_password']
        
        users = mongo.db.users
        user = users.find_one({'email': email})
        
        if user:
            password = user['password']
            print(password)
            
            if bcrypt.check_password_hash(password, password_candidate):
                # Passed
                session['logged_in'] = True
                session['email'] = email
                session['name'] = user['firstname']
                
                flash('You are now logged in', 'success')
                return redirect(url_for('browse'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
            
    return render_template("login.html")
    
# Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Unauthorized, please login', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap
    
# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login.html'))
    
@app.route('/browse')
@is_logged_in
def browse():
    return render_template('browse.html')
    
if __name__ == "__main__":
    app.secret_key='secret124'
    app.run(host=os.getenv('IP'),
            port=int(os.getenv('PORT')),
            debug=True)