import os
from flask import Flask, render_template, flash, redirect, request, url_for, session
from flask_bcrypt import Bcrypt
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config["MONGO_DBNAME"] = "the_worlds_cookbook"
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template("index.html", recipes=mongo.db.recipes.find())
    
    
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
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    print(form)
    if request.method == 'POST' and form.validate():
        users = mongo.db.users
        print(users)
        user = {
        'firstname': form.firstname.data,
        'lastname': form.lastname.data,
        'email': form.email.data,
        'password': bcrypt.generate_password_hash(form.password.data)}
        
        users.insert_one(user)
        
        flash('You are now registered and can login', 'success')
        
        return redirect(url_for('login'))
        
    return render_template('register.html', form=form)
    
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
                session
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
            
    return render_template("login.html")
    
if __name__ == "__main__":
    app.secret_key='secret123'
    app.run(host=os.getenv('IP'),
            port=int(os.getenv('PORT')),
            debug=True)