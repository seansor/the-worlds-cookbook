# The World's Cookbook

## An online repository of recipes created by people from all over the world

This is a recipe website which allows users to view recipes created by people
from every corner of the globe. The website production was sponsored by 
SOR Cooking Equipment Company for the benefit of users but also to promote
their brand of cooking equipment.

## UX

The website is for home cooks of all levels. The site provides users with a 
platform to view recipes and to create their own recipes which they can share with 
the world. The site aims to make good use of small infographics to give users
clear and concise information about each recipe, while also allowing users to add
more detail for the recipe descriptions and method.

### User Stories

* As a person looking for recipe inspiration I want to be able to be able to
  browse through all of the available recipes.
* As a user looking for specific recipes types I want to be able to filter by
  categories such as main ingredient and cuisine type.
* As a user who cooks recipes from the site I want to be able to provide feedback
  on the recipes I cook e.g via a "favourite" button.
* I want to keep track of which recipes I've favourited, so that i can easliy 
  identify those recipes again when I revisit the site.
* I want to contribute to the online database of recipes. I want to select an 
* add recipe option to create my own recipes and share them.
* I've forgotten to add something to my recipe or want to change it. I want
  to be able to do that via an edit button.
* I want remove a recipe that I created. I want to select a delete option to
  achieve this.

### Wireframes & Database Entity Relationship Diagrams

Wireframes and the Database Entity Relationship Diagram for the site are provided
in the project files in the "wireframes_erd" folder.

## Features

### Existing Features

* On the home page a user can create an account by selecting "Sign Up".
* If a user is already registered they can login by clicking on "Login".
* A user that tries to login who is not registered will recieve feedback to that
  effect.
* A user that is already registed, that tries to register again will recieve 
  feedback asking them to log in.
* A user that is not logged in can browse recipes but they will not have access
  to features such as 'favouriting', adding, editing or deleting recipes. Neither 
  will they have access to "My Recipes" which requires user authentication.
* Users can filter recipes in the "Browse" page by main ingredient type or 
  cuisine type.
* A user that is signed in will have access to the additonal feature as described
  above, namely; favouriting, adding, editing and deleting recipes. They will also
  have a "My Recipes" section which will contain all of the recipes they have 
  created.
* A logged in user will see a red heart on the recipes in the browse page that
  they have previously favourited.
* The browse page is sorted by default in order of most favourited. (Each user can
  only favourite an individual recipe once.)
* The Add Recipe page allows users to add a recipe.
* Form validation is in place on the forms through the use of WTForms. The code 
  for this validation can be viewed in the forms.py file.
* The Add Recipe page has a number of user interaction features beyond filling in
  the existing fields. These include:
    * The ability to choose the cuisine type from a select menu or
      input a new cuisine type by clicking on the "Add new Cuisine" button and
      entering it into the input dialog that appears.
    * The user can choose a main ingredient (which is used by the filters on the 
      browse page) from a select menu or add a new main ingredient if it is not
      in the list by clicking on the "Add new Ingredient" button and entering it
      into the input dialog that appears.
    * Add item buttons to add items to the ingredients and method. The number of
      items is limited to 20 for each ingredient section and 10 for method to 
      prevent users from having the ability to add infinite items.
    * Add/remove section button to add/remove new ingredient section. The user
      can use this feature to add another section if for example, besides the
      main meal the recipe also includes a dessert or a side. This allows them 
      to clearly differentiate the ingredients for each part of the meal. The 
      code that implements this functionality can be found in the main.js file at
      /static/js/main.js.
* There is an edit recipe button provided if users are logged in. This will only
  be shown on recipes the user has created. The features on the edit recipe page 
  are the same as the add recipe page. The additional JQuery required for this 
  functionality is also in main.js.
* There is a delete button provided so that users can delete recipes. Again, this 
  is only available on the user's recipes when logged in.
* A favourite button is provided on each recipe for logged in users. A user can 
  favourite a recipe by clicking on it and the favourite button will become
  highlighted. User can also "unfavourite" a recipe.
* A count of the amount of times each recipe is favourited is provided on each
  recipe.
* If a required utensil in the recipe matches a utensil in the company utensil 
  database, a link to that item in the store is provided.
* Each recipe also contains small infographics which tell the users:
    * Author
    * Last Edited Date
    * Prep Time
    * Cook Time
    * Difficulty
    * No. of Servings


### Features Left to Implement

* Additional Filters (e.g. total cook time, favourites)
* Sort By Functionality


## Technologies Used

#### HTML5
#### CSS3
#### Javascript

#### Bootstrap
The project uses [bootstrap 4.3.1](https://getbootstrap.com/docs/4.3/getting-started/introduction/) to assist in layout
and styling of the dashboard. [StartBootstrap](https://startbootstrap.com/themes/) was used to implement a particular bootstrap theme.

#### Fontawesome
The [Fontawesome](https://fontawesome.com/) icon toolkit was used to add icons to the website.

#### JQuery
The project uses [JQuery 3.4.1](https://jquery.com/) to simplify DOM manipulation.

#### Python
The backend of the application is built using [Python 3.6.8](https://www.python.org/downloads/release/python-368/)

#### Flask 
[Flask 1.1.1](https://palletsprojects.com/p/flask/) web application framework was used to assist in the backend development.

#### Flask-PyMongo
[Flask-PyMongo 2.3.0](https://flask-pymongo.readthedocs.io/en/latest/) was used to assist in interactions with the MongoDB database.

#### Flask-Bcrypt
[Flask-Bcrypt==0.7.1](https://flask-bcrypt.readthedocs.io/en/0.7.1/) was used to hash the user passwords.

#### Python-dotenv
[python-dotenv==0.10.3](https://pypi.org/project/python-dotenv/) was used to hide configuration variables.

#### WTForms
[WTForms 2.2.1](https://wtforms.readthedocs.io/en/stable/) was used to simplify form creation and validation.

#### Unittest

Python's [unittest](https://docs.python.org/3/library/unittest.html) framework was used for testing.


## Testing

Python's [unittest](https://docs.python.org/3/library/unittest.html) framework was used for automated testing.
All of the utility functions in the utils.py file were tested using automated testing. 
These tests can be found in the `test_utils.py` file in the main project directory.
To run these tests the test file should be at the same file directory level as the
utils.py file otherwise required dependencies will fail to import. To run the tests
type "`python3 -m unitest test_utils`" into the bash console (if running on linux).

All of the flask routes were tested using unittest. These tests can be found in 
the `test_app.py` file in the main project directory. To run these tests the test
file should be at the same file directory level as the app.py file otherwise the 
required dependencies will fail to import. To run the tests type
"`python3 -m unitest test_app`" into the bash console (if running on linux).


### Registration
* Error flashed if invalid email
* Error flashed if firstname or lastname isn't required length
* error flashed if passwords don't match


### Login Page
* Flashes error if invalid email or email or password don't match.

### Browse Page
* Favourite icon only appears on favourited recipes
* Recipes ordered according to most favourited
* Filter by cuisine works
    * No recipes shown for cuisines that do not yet exist.
    * French recipes shown when French selected.
    * British recipes shown when British selected.
    * Irish recipes shown when Irish selected.
** Filter by main ingredient works
    * No recipes shown for main ingredients that do not yet exist.
    * Chicken recipes shown when chicken selected.
    * Beed recipes shown when Beef selected.
    * Fish recipes shown when Fish selected.

### Recipe Page
* Favourite counter works correctly on recipes
* Favourite button works correctly
    * Adds recipe to user favourites array
    * Increases count by one
* Remove favourite button works correctly
    * Removes recipe to user favourites array
    * Increases count by one
* Edit button redirects to edit recipe (part of automated testing)
* Delete button deletes recipe and redirects to browse

### Add Recipe Page
* All fields rendered correctly
* Invalid feedback provided if url not provided for image
* Invalid feedback provided for description if not required amount of characters
* Ingredients require 3 items
* Add ingredient only allows 20 items per section
* Add section only allows 3 sections
* Add step to method only allows 10 steps
* steps left blank are ignored
* Add Recipe submits all recipe data to database correctly


### Edit Recipe
* All jQuery functionality works as described above in Add Recipe
* Correct data shown in fields
* Correct number of ingredient sections added as required
* Edit Recipe updated document with new values


### Responsiveness
The site was tested on different devices including a windows laptop, an IOS device
(iPhone 6) and an android device (OnePlus Phone). The website was also testing
using different browsers including Edge, Firefox and Chrome and the developer
tools in these browsers were also used to test the website's responsiveness.

The website displays well on all sizes of device although. On small screen sizes
the recipes in Browse display vertically and show less content.

Similarly on the recipe, add recipe and edit recipe pages the information displays 
vertically on small devices.

### Bugs
A number of bugs were caught during the testing process which were fixed. Some of
these were caused by the DOM manipulation on the add recipe and edit recipe pages.

There are a number of bugs that I am currently aware of that are yet to be fixed.
* One bug is in the filter options:
    * When changing between filter by main ingredient and cuisine all cuisines 
      are temporarly shown before an option in these categories is selected.
* Add Recipe/Edit Recipe
    * There is a bug caused by the validaion process of WTForms where if an invalid
      recipe submission is made, i.e. one field is not valid, on reload sometimes 
      the cuisine selector options do not reload.
* Favourite:
    * I've intermittently experienced an error where if clicked quickly in succession
      the favourite button might submit to the database twice. This seems to be due 
      to some asynchronous behaviour and should be resolved with an async/await 
      function or similar.

## Deployment
This site is hosted using Heroku, deployed directly from the master branch.
To deploy I set up a new new app in my [heroku dashboard](https://dashboard.heroku.com/apps).
I installed heroku CLI using the "`sudo snap install --classic heroku`" in the bash
terminal. I then logged in the heroku using the "heroku login" command and entered
my credentials. The heroku app gets it's files from git so it must be linked to 
the git repository. To do this I ran the command "`heroku git:remote -a the-worlds-cookbook`".
Then in order to push any changes commited to the git repository to the heroku
server I used the command "`git push heroku master`" in the bash terminal.
In order for the application to run on the heroku server the configuration
variables need to be set in the heroku app. Thess were set by accessing the project 
on heroku, going to settings and adding the variables to CONFIG VARS. The configuration 
variables for this project are: MONGO_URI, SECRET_KEY, PORT, and IP address. I also
set a DEBUG config var so that I can always have the application running in debug 
when developing and not have to remember to change it to DEBUG=FALSE for deployment.

To run locally, you can clone this repository directly into the editor of your
choice by pasting '`git clone https://github.com/seansor/the-worlds-cookbook.git`'
into your terminal. To cut ties with this GitHub repository, type "`git remote
rm origin`" into the terminal. 

#### Dependencies
It should be noted that this python project has a number of dependencies all of which 
are listed in the requirements.txt file in the main project folder. To ensure that 
only the dependencies needed are included in the requirements.txt file a virtual 
environment was set up of the project. This also ensures that the correct version 
of these packages is used for this project and updates to packages outside of the 
virtual environment will nto affect this projects dependencies. It is recommended
that anyone intending to clone this project and work on it locally should first
create a vitual environment. There is a built-in package in python called [venv](https://docs.python.org/3.6/library/venv.html#module-venv) 
which provides support for creating lightweight “virtual environments” with their
own site directories, optionally isolated from system site directories.
In order to use this module you should be using python 3.3 or higher. Nothing needs 
to be installed to run the venv package, it is part of the standard library.
To create a new virtual environment (in linux or mac) navigate to the folder you 
want the VE to be created in. (It is recommended to put this in the main project 
folder but note that the projetc files shoulf not go inside the venv folder created.
The VE should be able to be disposed of without affected the project files.)
Type the following command: "`python3 -m venv project_name`". As a convention my VE
was called venv so the command was "`python3 -m venv venv`". This will create a new 
folder venv. To activate the virtual env type source project_name/bin/activate. 
In this VE you can now install the required dependencies. So to create the 
requirements.txt file with the dependencies listed you can run "`pip freeze`" and 
redirect to requirements.txt by entering `pip freeze > requirements.txt`.


## Credits
### Content
The majority of the code is created by me. There is some code that has been taken
from other sources. The credits for these are below:
* All of the code in the "`vendor`" folder is 3rd party code taken from 
  [StartBootstrap](https://startbootstrap.com/themes/), which was used to 
  apply the basic css styling of the site. Additional styling also from the 
  same 3rd party vendor is in `static/css/business-casual.min.css`. (All other 
  css in this folder is custom.)

### Acknowledgements
I would like to acknowledge some of the help I got on flask fundamentals from 
[Traversy Media videos](https://www.youtube.com/channel/UC29ju8bIPH5as8OGnQzwJyA)
and some of the help on Virtual Environment venv from the [Corey Schafer videos](https://www.youtube.com/channel/UCCezIgC97PvUuR4_gbFUs5g)
. 
