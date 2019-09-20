import unittest
from app import mongo, ObjectId
from utils import time_to_hrs_and_mins, select_menu_options, utensil_select_menu_options

class TestUtilityFunctions(unittest.TestCase):
    """
    Test suite for utils (utility functions)
    """
    def test_converts_mins_to_hrs_and_mins(self):
        """
        Test to see that function returns array
        with hours at index 0 and mins at index 1
        """
        hours_mins = time_to_hrs_and_mins(70)
        self.assertEqual(hours_mins, [1,10])
        
        hours_mins = time_to_hrs_and_mins(50)
        self.assertEqual(hours_mins, [0,50])
        
        hours_mins = time_to_hrs_and_mins(50)
        self.assertNotEqual(hours_mins, [50])
        
        with self.assertRaises(TypeError):
            time_to_hrs_and_mins('string')
            
    
    def test_returns_array_zipObject_object_id(self):
        """
        Test to see that function returns array
        of document items, a zip object which as
        a list will be a list of tuples with
        string numbers and document items, and collection
        id which should be a BSON objectID.
        Lists should be sorted alphabetically
        """
        collection = mongo.db.difficulty
        document_attribute = "level"
        difficulty_choices=select_menu_options(collection, document_attribute)
        self.assertEqual(difficulty_choices[0], ["easy", "hard", "medium"])
        self.assertEqual(list(difficulty_choices[1]), [('1',"easy"), ("2","hard"), ("3","medium")])
        self.assertEqual(difficulty_choices[2], ObjectId('5d6fa1c71c9d440000fcc852'))
    
        
    def test_returns_zipObject_and_array(self):
        """
        Test to see that function returns a zip object
        which as a list will be a list of tuples with
        string numbers and document items, and an array
        of document items.
        Lists should be sorted alphabetically
        """
        utensil_choices = utensil_select_menu_options(mongo.db.company_utensils)
        select_menu_choices = list(utensil_choices[0])
        company_utensils = list(utensil_choices[1])
        self.assertEqual(select_menu_choices[0], ('1','chopping board'))
        self.assertEqual(select_menu_choices[1], ('2','electric whisk'))
        self.assertEqual(company_utensils[0], 'chopping board')
        self.assertEqual(company_utensils[1], 'electric whisk')
        