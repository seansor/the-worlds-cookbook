import os
from flask import Flask, render_template, flash, redirect, request, url_for, session
from flask_bcrypt import Bcrypt
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from functools import wraps
from datetime import datetime
import math
import itertools

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
    return redirect(url_for('login'))
    
@app.route('/browse')
@is_logged_in
def browse():
    recipes_mdb = mongo.db.recipes.find()
    # copy of cursor object as iterating over cursor in time_to_hrs_mins func
    # prevents iterable cursor from being passed to template 
    recipes_mdb_copy = mongo.db.recipes.find()
    # returns array of hour and minute tuples
    hrs_mins = time_to_hrs_and_mins(recipes_mdb_copy)
    recipes = zip(recipes_mdb, hrs_mins)
       
    return render_template('browse.html', recipes=recipes, hrs_mins=hrs_mins)
  
# Convert cooking time from minutes to hours & minutes  
def time_to_hrs_and_mins(recipes):
    hours_mins = []
    for recipe in recipes:
        total_time = recipe['cook_time'] + recipe['prep_time']
        if total_time < 60:
            hours_mins.append((0,total_time))
        else:
            hours = math.floor(round(total_time/60))
            minutes = total_time-(hours*60)
            hours_mins.append((hours, minutes))
    return hours_mins
        
@app.route('/recipe/<recipe_id>')
def get_recipe(recipe_id):
    recipe_mdb = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    ingredient_sections = list(recipe_mdb['ingredients'].keys())
    
    utensils_mdb = mongo.db.Utensils.find()
    utensils_list = list(utensils_mdb)
    company_utensils = utensils_list[0]['utensils']
    app.logger.info(utensils_list)
    return render_template('recipe.html', recipe=recipe_mdb, ingredient_sections=ingredient_sections, company_utensils = company_utensils)
    
@app.route('/add_recipe', methods=['GET', 'POST'])
@is_logged_in
def add_recipe():
    if 'recipe_image' in request.files:
    
        return 'Done!'
    
    
    
if __name__ == "__main__":
    # Remember to hide the secret key at the end
    app.secret_key='secret125'
    app.run(host=os.getenv('IP'),
            port=int(os.getenv('PORT')),
            debug=True)