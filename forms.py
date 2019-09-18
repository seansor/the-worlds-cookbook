from wtforms import Form, BooleanField, StringField, PasswordField, TextAreaField, IntegerField, SelectField, SelectMultipleField, FieldList, FormField, validators
from wtforms.fields.html5 import URLField

class RegistrationForm(Form):
    """ Register Form Class (WTForms)"""
    firstname = StringField('First Name', [validators.Length(min=4, max=15)])
    lastname = StringField('Last Name', [validators.Length(min=4, max=15)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

    
class addRecipe(Form):
    image = URLField('Recipe Image', [validators.InputRequired()])
    title = StringField('Title', [validators.Length(min=4, max=40), validators.InputRequired()])
    description = TextAreaField('Description', [validators.Length(min=15, max=150), validators.InputRequired()])
    cook_time = IntegerField('Cooking Time', [validators.InputRequired()])
    prep_time = IntegerField('Preparation Time', [validators.InputRequired()])
    serves = StringField('Servings', [validators.Length(min=1, max=12),validators.InputRequired()])
    cuisine = SelectField('Cuisine', coerce=int)
    main_ingredient = SelectField('Main Ingredient', coerce=int)
    meal_type = SelectField('Meal Type', coerce=int)
    difficulty = SelectField('Difficulty', coerce=int)
    is_vegetarian = BooleanField('Vegetarian')
    is_vegan = BooleanField('Vegan')
    ingredients = FieldList(StringField('Ingredients', [validators.InputRequired()]), min_entries=3)
    method = FieldList(TextAreaField('Method', [validators.InputRequired()]), min_entries=3)
    utensils = SelectMultipleField('Required Utensils')
    otherUtensils = StringField('Other Required Utensils', [validators.Length(max=100)])   

class editRecipe(Form):
    image = URLField('Recipe Image', [validators.InputRequired()])
    title = StringField('Title', [validators.Length(min=4, max=40), validators.InputRequired()])
    description = TextAreaField('Description', [validators.Length(min=15, max=150), validators.InputRequired()])
    cook_time = IntegerField('Cooking Time', [validators.InputRequired()])
    prep_time = IntegerField('Preparation Time', [validators.InputRequired()])
    serves = StringField('Servings', [validators.Length(min=1, max=12),validators.InputRequired()])
    cuisine = SelectField('Cuisine', coerce=int)
    main_ingredient = SelectField('Main Ingredient', coerce=int)
    meal_type = SelectField('Meal Type', coerce=int)
    difficulty = SelectField('Difficulty', coerce=int)
    is_vegetarian = BooleanField('Vegetarian')
    is_vegan = BooleanField('Vegan')
    ingredients = FieldList(StringField('Ingredients'))
    ingredients1 = FieldList(StringField('Ingredients1'))
    ingredients2 = FieldList(StringField('Ingredients2'))
    method = FieldList(TextAreaField('Method'))
    utensils = SelectMultipleField('Required Utensils')
    otherUtensils = StringField('Other Required Utensils', [validators.Length(max=100)])
    