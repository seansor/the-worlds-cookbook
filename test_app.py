import os
import unittest
from app import app, mongo

 
class RouteTests(unittest.TestCase):
    """
    setup and teardown
    flask route testing
    """
    
    # executed prior to each test
    def setUp(self):
        app.config['DEBUG'] = False
        app.config['MONGO_URI'] = 'mongodb+srv://' + \
            os.path.join(app.config['BASEDIR'], app.config['MONGO_DBNAME'])
        self.app = app.test_client()
 
    # executed after each test
    def tearDown(self):
        pass
 
 
    def test_index_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
    def test_login_page(self):
        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
           
    def test_register_page(self):
        response = self.app.get('/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
           
    def test_logout_page(self):
        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
    def test_browse_page(self):
        response = self.app.get('/recipes', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
    def test_recipe_page(self):
        response = self.app.get('/recipe/5d80d4b3514a531cd0f78cc5', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
    def test_edit_recipe_page(self):
        response = self.app.get('/edit_recipe/5d80d4b3514a531cd0f78cc5', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
    def test_add_recipe_page(self):
        response = self.app.get('/add_recipe', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
    
 
 
if __name__ == "__main__":
     unittest.main()
