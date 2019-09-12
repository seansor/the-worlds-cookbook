import os
from flask import Flask, render_template, flash, redirect, request, url_for, session
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from functools import wraps
from datetime import datetime
import math
#import itertools
from forms import *

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config["MONGO_DBNAME"] = "the_worlds_cookbook"
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template("index.html", recipes=mongo.db.recipes.find())
    

 
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
                session['id'] = str(user['_id'])
                
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
    user = mongo.db.users.find_one({'_id': ObjectId(session['id']) })
    user_favourites = user['favourites']
       
    return render_template('browse.html', recipes=recipes_mdb, user_favourites=user_favourites)
  
        
@app.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
def get_recipe(recipe_id):
    recipe_mdb = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    ingredient_sections = list(recipe_mdb['ingredients'].keys())
    
    utensils_mdb = mongo.db.Utensils.find()
    utensils_object_list = list(utensils_mdb)
    company_utensils = utensils_object_list[0]['utensils']
    
    if request.method == "POST":
        favourite= request.form.get('favourite')
        if favourite:
            mongo.db.users.update_one({'_id': ObjectId(session['id'])}, { "$push": { "favourites": ObjectId(recipe_id) } })
            mongo.db.recipes.update_one({'_id': ObjectId(recipe_id)}, { "$inc": { "favourite": 1 } })
        else:
            mongo.db.users.update_one({'_id': ObjectId(session['id'])}, { "$pull": { "favourites": ObjectId(recipe_id) } })
            mongo.db.recipes.update_one({'_id': ObjectId(recipe_id)}, { "$inc": { "favourite": -1 } })
        return redirect(url_for("get_recipe", recipe_id=recipe_mdb['_id']))
    
    user = mongo.db.users.find_one({'_id': ObjectId(session['id']) })
    user_favourites = user['favourites']
    
    return render_template('recipe.html', recipe=recipe_mdb, ingredient_sections=ingredient_sections, company_utensils = company_utensils, user_favourites=user_favourites)

#@app.route('/add_to_favourites')
    
    
    
@app.route('/add_recipe', methods=['GET', 'POST'])
@is_logged_in
def add_recipe():
    form = addRecipe(request.form)
    utensils_mdb = mongo.db.Utensils.find()
    utensils_object_list = list(utensils_mdb)
    company_utensils = (utensils_object_list[0]['utensils'])
    utensil_numbers = []
    for i in range(1, len(company_utensils)+1):
        utensil_numbers.append(i)
    choices = zip(utensil_numbers,company_utensils)
    form.utensils.choices = choices
    if request.method == "POST":
        recipes = mongo.db.recipes
        recipes.insert_one(request.form.to_dict())
        #image = request.form.get('image')
        #title = request.form.get('image')
        return redirect(url_for('browse'))
    else:
        return render_template('add_recipe.html', form = form)
    
    
    
if __name__ == "__main__":
    # Remember to hide the secret key at the end
    app.secret_key='secret125'
    app.run(host=os.getenv('IP'),
            port=int(os.getenv('PORT')),
            debug=True)