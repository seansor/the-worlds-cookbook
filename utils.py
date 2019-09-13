import math

# Convert cooking time from minutes to hours & minutes  
def time_to_hrs_and_mins(time_in_mins):
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