import math

# Convert cooking time from minutes to hours & minutes  
def time_to_hrs_and_mins(recipes):
    hours_mins = []
    
    for recipe in recipes:
        total_time = recipe['cook_time'] + recipe['prep_time']
        if total_time < 60:
            hours_mins.append((0,total_time))
        else:
            hours = math.floor(round(total_time/60))
            minutes = total_time-(hours*60)
            hours_mins.append((hours, minutes))
    return hours_mins