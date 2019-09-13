import os
from flask import Flask, render_template, flash, redirect, request, url_for, session
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from functools import wraps
from datetime import datetime
import math
from utils import *
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
    company_utensils.sort()
    utensil_numbers = []
    for i in range(1, len(company_utensils)+1):
        utensil_numbers.append(i)
    utensil_choices = zip(utensil_numbers,company_utensils)
    form.utensils.choices = utensil_choices
    
    main_ingredients_mdb = mongo.db.main_ingredient.find()
    main_ingredients_object_list = list(main_ingredients_mdb)
    main_ingredients = (main_ingredients_object_list[0]['ingredient'])
    main_ingredients.sort()
    main_ingredients_numbers = []
    for i in range(1, len(main_ingredients)+1):
        main_ingredients_numbers.append(i)
    main_ingredient_choices = zip(main_ingredients_numbers,main_ingredients)
    form.main_ingredient.choices = main_ingredient_choices
    
    cuisine_mdb = mongo.db.cuisine.find()
    cuisine_object_list = list(cuisine_mdb)
    cuisine = (cuisine_object_list[0]['cuisine_type'])
    cuisine.sort()
    cuisine_numbers = []
    for i in range(1, len(cuisine)+1):
        cuisine_numbers.append(i)
    cuisine_choices = zip(cuisine_numbers,cuisine)
    form.cuisine.choices = cuisine_choices
    
    
    if request.method == "POST":
        image = request.form.get('image')
        title = request.form.get('title')
        description = request.form.get('description')
        
        prep_mins = int(request.form.get('prep_time'))
        cook_mins = int(request.form.get('cook_time'))
        prep_time = time_to_hrs_and_mins(prep_mins)
        cook_time = time_to_hrs_and_mins(cook_mins)
        
        total_mins = (prep_mins+cook_mins)
        total_time = time_to_hrs_and_mins(total_mins)
        
        serves = request.form.get('serves')
        cuisine = request.form.get('cuisine')
        main_ingredient = request.form.get('main_ingredient')
        difficulty = request.form.get('difficulty')
        vegetarian = request.form.get('is_vegetarian')
        vegan = request.form.get('is_vegan')
        
        '''retrieve and format ingredients'''
        main=[]
        i=0
        while request.form.get("ingredients-"+str(i)):
            ingredient_main= request.form.get("ingredients-"+str(i))
            main.append(ingredient_main)
            i+=1
            
        ingredients = {"Main": main}
            
        if request.form.get("ingredients1-0"):
            section_name_1 = request.form.get('sectionName-1')
            side_1=[]
            i=0
            while request.form.get("ingredients1-"+str(i)):
                ingredient_side_1= request.form.get("ingredients1-"+str(i))
                side_1.append(ingredient_side_1)
                i+=1
            
            ingredients={"Main": main, section_name_1:side_1}
                
        if request.form.get("ingredients2-0"):
            section_name_2 = request.form.get('sectionName-2')
            side_2=[]
            i=0
            while request.form.get("ingredients2-"+str(i)):
                ingredient_side_2= request.form.get("ingredients2-"+str(i))
                side_2.append(ingredient_side_2)
                i+=1
             
            ingredients={"Main": main, section_name_1:side_1, section_name_2:side_2} 
        
        
        '''retrieve and format method steps'''  
        method = []
        
        i=0
        while request.form.get("method-"+str(i)):
            method_step= request.form.get("method-"+str(i))
            method.append(method_step)
            i+=1
        
        required_utensils=request.form.getlist('utensils')
        
        mongo.db.recipes.insert_one({
            'image': image,
            'title': title,
            'description': description,
            'prep_time':prep_time,
            'cook_time':cook_time,
            'total_time': total_time,
            'serves':serves,
            'cuisine':cuisine,
            'main_ingredient':main_ingredient,
            'difficulty':difficulty,
            'vegetarian':vegetarian,
            'vegan':vegan,
            'ingredients': ingredients,
            'method': method,
            'required_utensils': required_utensils,
            'author': ObjectId(session['id']),
            'last_edited': datetime.now(),
            'favourite': 0
        })
        
        
        
        return redirect(url_for('browse'))
    else:
        return render_template('add_recipe.html', form = form)
    
    
    
if __name__ == "__main__":
    # Remember to hide the secret key at the end
    app.secret_key='secret125'
    app.run(host=os.getenv('IP'),
            port=int(os.getenv('PORT')),
            debug=True)