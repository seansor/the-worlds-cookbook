import math
from forms import *


def time_to_hrs_and_mins(time_in_mins):
    '''Convert cooking time from minutes to hours & minutes '''
    hours_mins = []
    if time_in_mins < 60:
        hours_mins.append(0)
        hours_mins.append(time_in_mins)
    else:
        hours = math.floor(round(time_in_mins/60))
        minutes = time_in_mins-(hours*60)
        hours_mins.append(hours)
        hours_mins.append(minutes)
    return hours_mins
    

def select_menu_options(collection, document_attribute):
    '''retrieve collection and create tuples for wtforms select menus'''
    collection_mdb = collection.find()
    collection_data = list(collection_mdb)
    collection = collection_data[0][document_attribute]
    collection_id = collection_data[0]['_id']
    collection.sort()
    
    collection_numbers = []
    for i in range(1, len(collection)+1):
        collection_numbers.append(str(i))
    collection_choices = zip(collection_numbers,collection)
    
    return collection, collection_choices, collection_id
    
def utensil_select_menu_options(collection):
    '''retrieve collection and create tuples for wtforms select menus'''
    company_utensils_mdb = collection.find()
    company_utensils_data = list(company_utensils_mdb)
    company_utensil_links = company_utensils_data[0]['utensils']
    company_utensils = list(company_utensil_links.keys())
    company_utensils.sort()
    # create tuples with utensil names for select list (required by wtforms)
    utensil_numbers = []
    for i in range(1, len(company_utensils)+1):
        utensil_numbers.append(str(i))
    utensil_choices = zip(utensil_numbers,company_utensils)
    return utensil_choices, company_utensils
    
    