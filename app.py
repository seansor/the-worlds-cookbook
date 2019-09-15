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
    '''
    render browse page showing all recipes in database
    sorted by default by most favourited
    '''
    recipes_mdb = mongo.db.recipes.find()
    recipe_list = list(recipes_mdb)
    # sort recipes according to most favourited
    recipe_list.sort(key=lambda x: x['favourite'], reverse=True)
    
    user = mongo.db.users.find_one({'_id': ObjectId(session['id']) })
    user_favourites = user['favourites']
       
    return render_template('browse.html', recipes=recipe_list, user_favourites=user_favourites)
  
        
@app.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
def get_recipe(recipe_id):
    recipe_mdb = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    ingredient_sections = list(recipe_mdb['ingredients'].keys())
    
    company_utensils_mdb = mongo.db.company_utensils.find()
    #convert cursor object to list
    company_utensils_data = list(company_utensils_mdb)
    #select just the utensils object (ignore _id object)
    company_utensil_links = company_utensils_data[0]['utensils']
    #select just utensil names (ignore link)
    company_utensils = list(company_utensil_links.keys())
    app.logger.info(company_utensil_links['food processor'])
    
    
    if request.method == "POST":
        favourite= request.form.get('favourite')
        if favourite:
            mongo.db.users.update_one({'_id': ObjectId(session['id'])},
            { "$push": { "favourites": ObjectId(recipe_id) } })
            mongo.db.recipes.update_one({'_id': ObjectId(recipe_id)},
            { "$inc": { "favourite": 1 } })
        else:
            mongo.db.users.update_one({'_id': ObjectId(session['id'])},
            { "$pull": { "favourites": ObjectId(recipe_id) } })
            mongo.db.recipes.update_one({'_id': ObjectId(recipe_id)},
            { "$inc": { "favourite": -1 } })
        return redirect(url_for("get_recipe", recipe_id=recipe_mdb['_id']))
    
    user = mongo.db.users.find_one({'_id': ObjectId(session['id']) })
    user_favourites = user['favourites']
    
    return render_template('recipe.html', recipe=recipe_mdb,
                            ingredient_sections=ingredient_sections,
                            company_utensils = company_utensils,
                            company_utensil_links = company_utensil_links,
                            user_favourites=user_favourites)
    
@app.route('/add_recipe', methods=['GET', 'POST'])
@is_logged_in
def add_recipe():
    '''
    create add recipe form
    process add recipe form inputs 
    '''
    # create wtForms object
    form = addRecipe(request.form)
    
    # retrieve company utensil names and associated links
    company_utensils_mdb = mongo.db.company_utensils.find()
    company_utensils_data = list(company_utensils_mdb)
    company_utensil_links = company_utensils_data[0]['utensils']
    company_utensils = list(company_utensil_links.keys())
    company_utensils.sort()
    # create tuples with utensil names for select list (required by wtforms)
    utensil_numbers = []
    for i in range(1, len(company_utensils)+1):
        utensil_numbers.append(i)
    utensil_choices = zip(utensil_numbers,company_utensils)
    form.utensils.choices = utensil_choices
    
    # retrieve main ingredients
    main_ingredients_mdb = mongo.db.main_ingredient.find()
    main_ingredients_object_list = list(main_ingredients_mdb)
    main_ingredients = (main_ingredients_object_list[0]['ingredient'])
    main_ingredients_id = (main_ingredients_object_list[0]['_id'])
    main_ingredients.sort()
    
    # create tuples with main ingredients for select list (required by wtforms)
    main_ingredients_numbers = []
    for i in range(1, len(main_ingredients)+1):
        main_ingredients_numbers.append(i)
    main_ingredient_choices = zip(main_ingredients_numbers,main_ingredients)
    form.main_ingredient.choices = main_ingredient_choices
    
    #retrieve cuisine types
    cuisine_mdb = mongo.db.cuisine.find()
    cuisine_object_list = list(cuisine_mdb)
    cuisines = (cuisine_object_list[0]['cuisine_type'])
    cuisines_object_id = (cuisine_object_list[0]['_id'])
    cuisines.sort()
    
    # create tuples with main ingredients for select list (required by wtforms)
    cuisine_numbers = []
    for i in range(1, len(cuisines)+1):
        cuisine_numbers.append(i)
    cuisine_choices = zip(cuisine_numbers,cuisines)
    form.cuisine.choices = cuisine_choices
    
    # retrieve meal types
    meal_type_mdb = mongo.db.meal_type.find()
    meal_type_object_list = list(meal_type_mdb)
    meal_types = (meal_type_object_list[0]['type'])
    meal_types.sort()
    meal_type_numbers = []
    
    # create tuples with meal types for select list (required by wtforms)
    for i in range(1, len(meal_types)+1):
        meal_type_numbers.append(i)
    meal_type_choices = zip(meal_type_numbers,meal_types)
    form.meal_type.choices = meal_type_choices
    
    # retrieve difficulty level
    difficulty_mdb = mongo.db.difficulty.find()
    difficulty_object_list = list(difficulty_mdb)
    difficulty_levels = (difficulty_object_list[0]['level'])
    difficulty_levels.sort()
    
    # create tuples with difficulty level for select list (required by wtforms)
    difficulty_numbers = []
    for i in range(1, len(difficulty_levels)+1):
        difficulty_numbers.append(i)
    difficulty_choices = zip(difficulty_numbers,difficulty_levels)
    form.difficulty.choices = difficulty_choices
    
    # Parse data submitted by add_recipe form andsubmit to database
    if request.method == "POST":
        image = request.form.get('image')
        title = request.form.get('title')
        description = request.form.get('description')
        
        prep_mins = int(request.form.get('prep_time'))
        prep_time = time_to_hrs_and_mins(prep_mins)
        
        cook_mins = int(request.form.get('cook_time'))
        cook_time = time_to_hrs_and_mins(cook_mins)
        
        total_mins = (prep_mins+cook_mins)
        total_time = time_to_hrs_and_mins(total_mins)
        
        serves = request.form.get('serves')
        
        # Get selected cuisine
        # If new cuisine added by user, add new item to database 
        if request.form.get('otherCuisine'):
            selected_cuisine = request.form.get('otherCuisine')
            if selected_cuisine.lower() not in cuisines:
                mongo.db.cuisine.update_one({'_id': ObjectId(cuisines_object_id)},
                { "$push": { "cuisine_type": selected_cuisine.lower() } })
        else:
            cuisine_number = request.form.get('cuisine')
            all_cuisines = dict(cuisine_choices)
            selected_cuisine = all_cuisines[int(cuisine_number)]
        
        # Get selected main ingredient
        # If new main ingredient added by user, add new item to database    
        if request.form.get('otherMain_ingredient'):
            selected_main_ingredient = request.form.get('otherMain_ingredient')
            if selected_main_ingredient.lower() not in main_ingredients:
                mongo.db.main_ingredient.update_one({'_id': ObjectId(main_ingredients_id)},
                { "$push": { "ingredient": selected_main_ingredient.lower() } })
        else:
            main_ingredient_number = request.form.get('main_ingredient')
            all_main_ingredients = dict(main_ingredient_choices)
            selected_main_ingredient = all_main_ingredients[int(main_ingredient_number)]
        
        # Get difficulty level selected
        difficulty_number = request.form.get('difficulty')
        all_difficulty_levels = dict(difficulty_choices)
        selected_difficulty_level = all_difficulty_levels[int(difficulty_number)]
        
        # Get meal type selected
        meal_type_number = request.form.get('meal_type')
        all_meal_types = dict(meal_type_choices)
        selected_meal_type = all_meal_types[int(meal_type_number)]
        
        
        vegetarian = request.form.get('is_vegetarian')
        vegan = request.form.get('is_vegan')
        
        # retrieve and format ingredients
        # get main ingredients
        main=[]
        i=0
        while request.form.get("ingredients-"+str(i)):
            ingredient_main= request.form.get("ingredients-"+str(i))
            main.append(ingredient_main)
            i+=1
            
        ingredients = {"Main": main}
        
        # if second ingredient section added, get section ingredients    
        if request.form.get("ingredients1-0"):
            section_name_1 = request.form.get('sectionName-1')
            side_1=[]
            i=0
            while request.form.get("ingredients1-"+str(i)):
                ingredient_side_1= request.form.get("ingredients1-"+str(i))
                side_1.append(ingredient_side_1)
                i+=1
            
            ingredients={"Main": main, section_name_1:side_1}
        
        # if third ingredient section added, get section ingredients         
        if request.form.get("ingredients2-0"):
            section_name_2 = request.form.get('sectionName-2')
            side_2=[]
            i=0
            while request.form.get("ingredients2-"+str(i)):
                ingredient_side_2= request.form.get("ingredients2-"+str(i))
                side_2.append(ingredient_side_2)
                i+=1
             
            ingredients={"Main": main, section_name_1:side_1, section_name_2:side_2} 
        
        
        #retrieve and format method steps
        method = []
        i=0
        while request.form.get("method-"+str(i)):
            method_step= request.form.get("method-"+str(i))
            method.append(method_step)
            i+=1
        
        # retrieve and format method steps
        # get required utensils selected by user
        required_utensils=[]
        all_company_utensils=dict(utensil_choices)
        selected_utensils=request.form.getlist('utensils')
        for selected_utensil in selected_utensils:
            required_utensil=all_company_utensils[int(selected_utensil)]
            required_utensils.append(required_utensil)
        
        # get other utensils input by user
        other_utensils_user_input = request.form.get('otherUtensils')
        other_utensils = [word.strip() for word in other_utensils_user_input.split(',')]
        for utensil in other_utensils:
            required_utensils.append(utensil)
        
        # add recipe to database
        mongo.db.recipes.insert_one({
            'image': image,
            'title': title,
            'description': description,
            'prep_time':prep_time,
            'cook_time':cook_time,
            'total_time': total_time,
            'serves':serves,
            'cuisine':selected_cuisine,
            'main_ingredient':selected_main_ingredient,
            'meal_type':selected_meal_type,
            'difficulty':selected_difficulty_level,
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