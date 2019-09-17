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
    
    mongo.db.recipes.remove({'title': "test"})
       
    return render_template('browse.html', recipes=recipe_list, user_favourites=user_favourites)
  
        
@app.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
def get_recipe(recipe_id):
    '''
    Get selected recipe
    Allow signed in users to favourite recipes
    '''
    recipe_mdb = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    ingredient_sections = list(recipe_mdb['ingredients'].keys())
    
    author_id = recipe_mdb['author']
    author = mongo.db.users.find_one({'_id': ObjectId(author_id) })
    fullname = author['firstname']+' '+author['lastname']
    
    app.logger.info(recipe_mdb['last_edited'])
    last_edited = recipe_mdb['last_edited'].strftime("%d-%m-%y")
    
    # retrieve company utensil names and associated links
    company_utensils_mdb = mongo.db.company_utensils.find()
    company_utensils_data = list(company_utensils_mdb)
    company_utensil_links = company_utensils_data[0]['utensils']
    company_utensils = list(company_utensil_links.keys())
    
    # add/remove recipe from user favourites
    # count number of times recipe has been favourited
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
                            user_favourites=user_favourites, author=fullname, last_edited=last_edited)
    
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
    # create tuples with main ingredients for select list (required by wtforms)
    main_ingredient_options=select_menu_options(form, mongo.db.main_ingredient, "ingredient")
    
    main_ingredients = main_ingredient_options[0]
    form.main_ingredient.choices = main_ingredient_options[1]
    main_ingredient_choices = main_ingredient_options[1]
    main_ingredients_id = main_ingredient_options[2]
    
    #retrieve cuisine types
    # create tuples with main ingredients for select list (required by wtforms)
    cuisine_options=select_menu_options(form, mongo.db.cuisine, "cuisine_type")
    
    cuisines = cuisine_options[0]
    form.cuisine.choices = cuisine_options[1]
    cuisine_choices = cuisine_options[1]
    cuisines_id = cuisine_options[2]
    
    
    # retrieve meal types
    # create tuples with meal types for select list (required by wtforms)
    meal_type_options=select_menu_options(form, mongo.db.meal_type, "type")
    meal_types = meal_type_options[0]
    form.meal_type.choices = meal_type_options[1]
    meal_type_choices = meal_type_options[1]
    
    
    # meal_types_mdb = mongo.db.meal_type.find()
    # meal_types_data = list(meal_types_mdb)
    # meal_types = (meal_types_data[0]['type'])
    # meal_types.sort()
    
    
    
    # retrieve difficulty level
    # create tuples with difficulty level for select list (required by wtforms)
    difficulty_level_options=select_menu_options(form, mongo.db.difficulty, "level")
    difficulty_levels = difficulty_level_options[0]
    form.difficulty.choices = difficulty_level_options[1]
    difficulty_level_choices = difficulty_level_options[1]
    
    
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
                mongo.db.cuisine.update_one({'_id': ObjectId(cuisines_id)},
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
        difficulty_level_number = request.form.get('difficulty')
        all_difficulty_levels = dict(difficulty_level_choices)
        selected_difficulty_level = all_difficulty_levels[int(difficulty_level_number)]
        
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
    
@app.route('/edit_recipe/<recipe_id>', methods=['GET', 'POST'])
@is_logged_in
def edit_recipe(recipe_id):
    recipe_mdb = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    form = editRecipe(request.form)
    
    form.image.data = recipe_mdb['image']
    form.title.data = recipe_mdb['title']
    form.description.data = recipe_mdb['description']
    form.prep_time.data = (recipe_mdb['prep_time'][0]*60)+recipe_mdb['prep_time'][1]
    form.cook_time.data = (recipe_mdb['cook_time'][0]*60)+recipe_mdb['cook_time'][1]
    form.serves.data = recipe_mdb['serves']
    
    cuisine_options=select_menu_options(form, mongo.db.cuisine, "cuisine_type")
    form.cuisine.choices = cuisine_options[1]
    app.logger.info(cuisine_options[1])
    cuisine_choices = cuisine_options[0]
    for cuisine in cuisine_choices:
        if recipe_mdb['cuisine'] == cuisine:
            form.cuisine.data= str(cuisine_choices.index(cuisine)+1)

    
    main_ingredient_options=select_menu_options(form, mongo.db.main_ingredient, "ingredient")
    form.main_ingredient.choices = main_ingredient_options[1]
    main_ingredient_choices = main_ingredient_options[0]
    for main_ingredient in main_ingredient_choices:
        if recipe_mdb['main_ingredient'] == main_ingredient:
            form.main_ingredient.data = str(main_ingredient_choices.index(main_ingredient)+1)
            

    meal_type_options=select_menu_options(form, mongo.db.meal_type, "type")
    form.meal_type.choices = meal_type_options[1]
    app.logger.info(meal_type_options[1])
    meal_type_choices = meal_type_options[0]
    for meal_type in meal_type_choices:
        if recipe_mdb['meal_type'] == meal_type:
            app.logger.info(meal_type_choices.index(meal_type)+1)
            form.meal_type.data = str(meal_type_choices.index(meal_type)+1)
            
    
    difficulty_level_options=select_menu_options(form, mongo.db.difficulty, "level")
    form.difficulty.choices = difficulty_level_options[1]
    difficulty_level_choices = difficulty_level_options[0]
    for difficulty_level in difficulty_level_choices:
        if recipe_mdb['difficulty'] == difficulty_level:
            form.difficulty.data = str(difficulty_level_choices.index(difficulty_level)+1)
    
    
    form.is_vegetarian.data = recipe_mdb['vegetarian']
    form.is_vegan.data = recipe_mdb['vegan']
    
    recipe_sections=list(recipe_mdb['ingredients'].keys())
    
    for section in recipe_sections:
        app.logger.info(section)
        ingredients = recipe_mdb['ingredients'][section]
        if recipe_sections.index(section) == 0:
            for ingredient in ingredients:
                form.ingredients.append_entry(ingredient)
        elif recipe_sections.index(section) == 1:
            for ingredient in ingredients:
                form.ingredients1.append_entry(ingredient)
        else:
            for ingredient in ingredients:
                form.ingredients2.append_entry(ingredient)
            
    return render_template('edit_recipe.html', form=form, recipe_sections=recipe_sections)
    
if __name__ == "__main__":
    # Remember to hide the secret key at the end
    app.secret_key='secret125'
    app.run(host=os.getenv('IP'),
            port=int(os.getenv('PORT')),
            debug=True)