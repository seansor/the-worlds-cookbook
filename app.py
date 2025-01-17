import os
from datetime import datetime
from flask import Flask, render_template, flash, redirect, request, url_for, session
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from bson.objectid import ObjectId
from functools import wraps
from utils import time_to_hrs_and_mins, select_menu_options, utensil_select_menu_options
from forms import RegistrationForm, addRecipe, editRecipe

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config["MONGO_DBNAME"] = os.getenv("DB_NAME")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.secret_key=os.getenv("SECRET_KEY")
app.config["BASEDIR"] = os.getenv("BASEDIR")

mongo = PyMongo(app)


@app.route('/')
def index():
    return render_template("index.html", recipes=mongo.db.recipes.find())
  
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User Registration"""
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
    
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User Login"""
    if request.method == 'POST':
        email = request.form['user_email']
        password_candidate = request.form['user_password']
        
        users = mongo.db.users
        user = users.find_one({'email': email})
        
        if user:
            password = user['password']
            
            if bcrypt.check_password_hash(password, password_candidate):
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
    

def is_logged_in(f):
    """Check if user is logged in"""
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Unauthorized, please login', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap
    

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

    
@app.route('/recipes')
def browse():
    """
    render browse page showing all recipes in database
    sorted by default by most favourited
    """
    recipes_mdb = mongo.db.recipes.find()
    recipe_list = list(recipes_mdb)
    # sort recipes according to most favourited
    recipe_list.sort(key=lambda x: x['favourite'], reverse=True)
    
    cuisines = sorted((mongo.db.cuisine.find())[0]['cuisine_type'])
    
    main_ingredients = list(mongo.db.main_ingredient.find())[0]['ingredient']
    
    if 'logged_in' in session:
        user = mongo.db.users.find_one({'_id': ObjectId(session['id']) })
        user_favourites = user['favourites']
        return render_template('browse.html', recipes=recipe_list, user_favourites=user_favourites, cuisines=cuisines, main_ingredients=main_ingredients)
    else:
        return render_template('browse.html', recipes=recipe_list, cuisines=cuisines, main_ingredients=main_ingredients)


@app.route('/my_recipes')
@is_logged_in
def my_recipes():
    """render my_recipes page
        page shows all recipes in database created by current user
        sorted by default by most recent"""
    recipes_mdb = mongo.db.recipes.find()
    recipe_list = list(recipes_mdb)
    # sort recipes according to most favourited
    recipe_list.sort(key=lambda x: x['last_edited'], reverse=True)
    
    #user = mongo.db.users.find_one({'_id': ObjectId(session['id']) })
    #user_favourites = user['favourites']
    return render_template('my_recipes.html', recipes=recipe_list, user_id=ObjectId(session['id']))

        
@app.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
def get_recipe(recipe_id):
    """
    Get selected recipe
    Allow signed in users to favourite recipes
    """
    recipe_mdb = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    ingredient_sections = list(recipe_mdb['ingredients'].keys())
    
    author_id = recipe_mdb['author']
    author = mongo.db.users.find_one({'_id': ObjectId(author_id) })
    fullname = author['firstname']+' '+author['lastname']
    
    last_edited = recipe_mdb['last_edited'].strftime("%d-%m-%y")
    
    # retrieve company utensil names and associated links
    company_utensils_mdb = mongo.db.company_utensils.find()
    company_utensils_data = list(company_utensils_mdb)
    company_utensil_links = company_utensils_data[0]['utensils']
    company_utensils = list(company_utensil_links.keys())
    
    # add/remove recipe from user favourites
    # count number of times recipe has been favourited
    if 'logged_in' in session:
        user = mongo.db.users.find_one({'_id': ObjectId(session['id']) })
        user_favourites = user['favourites']
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
    
        return render_template('recipe.html', recipe=recipe_mdb,
                            ingredient_sections=ingredient_sections,
                            company_utensils = company_utensils,
                            company_utensil_links = company_utensil_links,
                            user_favourites=user_favourites, author=fullname, last_edited=last_edited, session=session, user_id=ObjectId(session['id']))
    else:
        return render_template('recipe.html', recipe=recipe_mdb,
                            ingredient_sections=ingredient_sections,
                            company_utensils = company_utensils,
                            company_utensil_links = company_utensil_links,
                            author=fullname, last_edited=last_edited, session=session)

    
@app.route('/add_recipe', methods=['GET', 'POST'])
@is_logged_in
def add_recipe():
    """
    create add recipe form
    process add recipe form inputs 
    """
    # create wtForms object
    form = addRecipe(request.form)
    
    # retrieve company utensil names and associated links
    # get required utensils and company utensils
    utensil_options = utensil_select_menu_options(mongo.db.company_utensils)
    utensil_choices = utensil_options[0]
    company_utensils = utensil_options[1]
    form.utensils.choices = utensil_choices
    
    # retrieve main ingredients
    # create tuples with main ingredients for select list (required by wtforms)
    main_ingredient_options=select_menu_options(mongo.db.main_ingredient, "ingredient")
    main_ingredients = main_ingredient_options[0]
    form.main_ingredient.choices = main_ingredient_options[1]
    main_ingredient_choices = main_ingredient_options[1]
    main_ingredients_id = main_ingredient_options[2]
    
    # retrieve cuisine types
    # create tuples with main ingredients for select list (required by wtforms)
    cuisine_options=select_menu_options(mongo.db.cuisine, "cuisine_type")
    cuisines = cuisine_options[0]
    form.cuisine.choices = cuisine_options[1]
    cuisine_choices = cuisine_options[1]
    cuisines_id = cuisine_options[2]
    
    # retrieve meal types
    # create tuples with meal types for select list (required by wtforms)
    meal_type_options=select_menu_options(mongo.db.meal_type, "type")
    form.meal_type.choices = meal_type_options[1]
    meal_type_choices = meal_type_options[1]

    # retrieve difficulty level
    # create tuples with difficulty level for select list (required by wtforms)
    difficulty_level_options=select_menu_options(mongo.db.difficulty, "level")
    form.difficulty.choices = difficulty_level_options[1]
    difficulty_level_choices = difficulty_level_options[1]
    
    # Parse data submitted by add_recipe form andsubmit to database
    if request.method == "POST" and form.validate():
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
            selected_cuisine = request.form.get('otherCuisine').lower()
            if selected_cuisine not in cuisines:
                mongo.db.cuisine.update_one({'_id': ObjectId(cuisines_id)},
                { "$push": { "cuisine_type": selected_cuisine } })
        else:
            cuisine_options=select_menu_options(mongo.db.cuisine, "cuisine_type")
            cuisine_choices = cuisine_options[1]
            cuisine_number = request.form.get('cuisine')
            all_cuisines = dict(cuisine_choices)
            selected_cuisine = all_cuisines[cuisine_number]
        
        # Get selected main ingredient
        # If new main ingredient added by user, add new item to database    
        if request.form.get('otherMain_ingredient'):
            selected_main_ingredient = request.form.get('otherMain_ingredient')
            if selected_main_ingredient.lower() not in main_ingredients:
                mongo.db.main_ingredient.update_one({'_id': ObjectId(main_ingredients_id)},
                { "$push": { "ingredient": selected_main_ingredient.lower() } })
        else:
            main_ingredient_options=select_menu_options(mongo.db.main_ingredient, "ingredient")
            main_ingredient_choices = main_ingredient_options[1]
            main_ingredient_number = request.form.get('main_ingredient')
            all_main_ingredients = dict(main_ingredient_choices)
            selected_main_ingredient = all_main_ingredients[main_ingredient_number]
        
        # Get difficulty level selected
        difficulty_level_options=select_menu_options(mongo.db.difficulty, "level")
        difficulty_level_choices = difficulty_level_options[1]
        difficulty_level_number = request.form.get('difficulty')
        all_difficulty_levels = dict(difficulty_level_choices)
        selected_difficulty_level = all_difficulty_levels[difficulty_level_number]
        
        # Get meal type selected
        meal_type_options=select_menu_options(mongo.db.meal_type, "type")
        meal_type_choices = meal_type_options[1]
        meal_type_number = request.form.get('meal_type')
        all_meal_types = dict(meal_type_choices)
        selected_meal_type = all_meal_types[str(meal_type_number)]
        
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
        
        
        # retrieve and format method steps
        method = []
        i=0
        while request.form.get("method-"+str(i)):
            method_step= request.form.get("method-"+str(i))
            method.append(method_step)
            i+=1
            
        # get required utensils and company utensils
        utensil_options = utensil_select_menu_options(mongo.db.company_utensils)
        utensil_choices = utensil_options[0]
        company_utensils = utensil_options[1]
        form.utensils.choices = utensil_choices
        
        required_utensils=[]
        selected_utensils=request.form.getlist('utensils')
        for selected_utensil in selected_utensils:
            required_utensil=company_utensils[int(selected_utensil)]
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
    """
    Create edit recipe form
    Fill in form fields with original data
    """
    recipe_mdb = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    form = editRecipe(request.form)
    
    form.image.data = recipe_mdb['image']
    form.title.data = recipe_mdb['title']
    form.description.data = recipe_mdb['description']
    form.prep_time.data = (recipe_mdb['prep_time'][0]*60)+recipe_mdb['prep_time'][1]
    form.cook_time.data = (recipe_mdb['cook_time'][0]*60)+recipe_mdb['cook_time'][1]
    form.serves.data = recipe_mdb['serves']
    
    # get cuisine options and set selected option
    cuisine_options=select_menu_options(mongo.db.cuisine, "cuisine_type")
    cuisine_choices = cuisine_options[1]
    form.cuisine.choices = cuisine_choices
    cuisines = cuisine_options[0]
    for cuisine in cuisines:
        if recipe_mdb['cuisine'] == cuisine:
            form.cuisine.data= str(cuisines.index(cuisine)+1)
    cuisines_id = cuisine_options[2]
    
    # get main_ingredient options and set selected option
    main_ingredient_options=select_menu_options(mongo.db.main_ingredient, "ingredient")
    main_ingredient_choices = main_ingredient_options[1]
    form.main_ingredient.choices = main_ingredient_choices
    main_ingredients = main_ingredient_options[0]
    for main_ingredient in main_ingredients:
        if recipe_mdb['main_ingredient'] == main_ingredient:
            form.main_ingredient.data = str(main_ingredients.index(main_ingredient)+1)
    main_ingredients_id = main_ingredient_options[2]

    # get meal_type options and set selected option
    meal_type_options=select_menu_options(mongo.db.meal_type, "type")
    form.meal_type.choices = meal_type_options[1]
    meal_type_choices = meal_type_options[0]
    for meal_type in meal_type_choices:
        if recipe_mdb['meal_type'] == meal_type:
            form.meal_type.data = str(meal_type_choices.index(meal_type)+1)
    
    # get difficulty options and set selected option
    difficulty_level_options=select_menu_options(mongo.db.difficulty, "level")
    form.difficulty.choices = difficulty_level_options[1]
    difficulty_level_choices = difficulty_level_options[0]
    for difficulty_level in difficulty_level_choices:
        if recipe_mdb['difficulty'] == difficulty_level:
            form.difficulty.data = str(difficulty_level_choices.index(difficulty_level)+1)
    
    
    form.is_vegetarian.data = recipe_mdb['vegetarian']
    form.is_vegan.data = recipe_mdb['vegan']
    
    # get ingredients
    # check for number of sections and set section names
    recipe_sections=list(recipe_mdb['ingredients'].keys())
    if len(recipe_sections) > 1:
        section_name_1 = recipe_sections[1]
        if len(recipe_sections) > 2 :
            section_name_2 = recipe_sections[2]
        else:
            section_name_2 = ""
    else:
        section_name_2 = ""
        section_name_1 = ""
    
    for section in recipe_sections:
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
    
    # set method steps            
    method = recipe_mdb['method']
    for step in method:
        form.method.append_entry(step)
    
    # get required utensils and company utensils
    utensil_options = utensil_select_menu_options(mongo.db.company_utensils)
    form.utensils.choices = utensil_options[0]
    company_utensils = utensil_options[1]
    
    # set selected options from utensil dropdown (company utensils)
    # add otehr utensils to other utensils field
    required_utensils=recipe_mdb['required_utensils']
    form.utensils.data = []
    other_utensils = []
    for utensil in required_utensils:
        if utensil in company_utensils:
            form.utensils.data.append(str(company_utensils.index(utensil)+1))
        else:
            other_utensils.append(utensil)
    form.otherUtensils.data = ','.join(map(str, other_utensils))
    
    
    # Parse data submitted by add_recipe form andsubmit to database
    if request.method == "POST" and form.validate():
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
            selected_cuisine = (request.form.get('otherCuisine')).lower()
            if selected_cuisine not in cuisines:
                mongo.db.cuisine.update_one({'_id': ObjectId(cuisines_id)},
                { "$push": { "cuisine_type": selected_cuisine } })
        else:
            cuisine_options=select_menu_options(mongo.db.cuisine, "cuisine_type")
            cuisine_choices = cuisine_options[1]
            cuisine_number = request.form.get('cuisine')
            all_cuisines = dict(cuisine_choices)
            selected_cuisine = all_cuisines[cuisine_number]
        
        # Get selected main ingredient
        # If new main ingredient added by user, add new item to database    
        if request.form.get('otherMain_ingredient'):
            selected_main_ingredient = request.form.get('otherMain_ingredient')
            if selected_main_ingredient.lower() not in main_ingredients:
                mongo.db.main_ingredient.update_one({'_id': ObjectId(main_ingredients_id)},
                { "$push": { "ingredient": selected_main_ingredient.lower() } })
        else:
            main_ingredient_options=select_menu_options(mongo.db.main_ingredient, "ingredient")
            main_ingredient_choices = main_ingredient_options[1]
            main_ingredient_number = request.form.get('main_ingredient')
            all_main_ingredients = dict(main_ingredient_choices)
            selected_main_ingredient = all_main_ingredients[main_ingredient_number]
        
        # Get difficulty level selected
        difficulty_level_options=select_menu_options(mongo.db.difficulty, "level")
        difficulty_level_choices = difficulty_level_options[1]
        difficulty_level_number = request.form.get('difficulty')
        all_difficulty_levels = dict(difficulty_level_choices)
        selected_difficulty_level = all_difficulty_levels[difficulty_level_number]
        
        # Get meal type selected
        meal_type_options=select_menu_options(mongo.db.meal_type, "type")
        meal_type_choices=meal_type_options[1]
        meal_type_number = request.form.get('meal_type')
        all_meal_types = dict(meal_type_choices)
        selected_meal_type = all_meal_types[str(meal_type_number)]
        
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
            if request.form.get('sectionName-1'):
                section_name_1 = request.form.get('sectionName-1')
            else:
                section_name_1
            side_1=[]
            i=0
            while request.form.get("ingredients1-"+str(i)):
                ingredient_side_1= request.form.get("ingredients1-"+str(i))
                side_1.append(ingredient_side_1)
                i+=1
            
            ingredients={"Main": main, section_name_1:side_1}
        
        # if third ingredient section added, get section ingredients         
        if request.form.get("ingredients2-0"):
            if request.form.get('sectionName-2'):
                section_name_2 = request.form.get('sectionName-2')
            else:
                section_name_1
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
            
        # get required utensils and company utensils
        utensil_options = utensil_select_menu_options(mongo.db.company_utensils)
        utensil_choices = utensil_options[0]
        company_utensils = utensil_options[1]
        
        # get required utensils selected by user
        required_utensils=[]
        all_company_utensils=dict(utensil_choices)
        selected_utensils=request.form.getlist('utensils')
        for selected_utensil in selected_utensils:
            required_utensil=all_company_utensils[selected_utensil]
            required_utensils.append(required_utensil)
        
        # get other utensils input by user
        other_utensils_user_input = request.form.get('otherUtensils')
        other_utensils = [word.strip() for word in other_utensils_user_input.split(',')]
        for utensil in other_utensils:
            required_utensils.append(utensil)
            
        favourite = recipe_mdb['favourite']
        
        # add updated recipe to database
        mongo.db.recipes.update_one({'_id': ObjectId(recipe_id)}, {'$set':{
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
            'favourite': favourite
            }
        })
        return redirect(url_for('browse'))
    else:
        return render_template('edit_recipe.html', form=form, recipe_sections=recipe_sections, recipe=recipe_mdb, section_name1=section_name_1, section_name2=section_name_2)


@app.route('/delete/<recipe_id>')
@is_logged_in
def delete(recipe_id):
    mongo.db.recipes.remove({'_id': ObjectId(recipe_id)}, {
     'justOne': True})
    return redirect(url_for('browse'))

    
if __name__ == "__main__":
    app.run(host=os.getenv('IP'),
            port=int(os.getenv('PORT')),
            debug=os.getenv("DEBUG"))