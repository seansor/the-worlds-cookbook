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
    

def select_menu_options(form, collection, document_attribute):
    '''retrieve collection and create tuples for wtforms select menus'''
    collection_mdb = collection.find()
    collection_data = list(collection_mdb)
    collection = collection_data[0][document_attribute]
    collection_id = collection_data[0]['_id']
    collection.sort()
    
    collection_numbers = []
    for i in range(1, len(collection)+1):
        collection_numbers.append(i)
    collection_choices = zip(collection_numbers,collection)
    
    return collection, collection_choices, collection_id
    
    