import datetime
import calendar
from models import Restaurant, Entry
import requests
from dotenv import load_dotenv
import os

# return None if invalid year month
def generateCalendarHTML(db, user_id, year=None, month=None):
    start = None
    try:
        if year != None and month != None:
            start = datetime.datetime(int(year), int(month), 1).date()
        else:
            start = datetime.datetime.now().date().replace(day=1)
    except:
        return None
    
    # add 32 days from the 1st and then replace day to 1 to get the 1st of next month
    end = (start + datetime.timedelta(days=32)).replace(day=1)
    
    entries = get_entries_for_user(db, user_id, start, end)
    
    html = f"""<div class="container text-center">
	<h1>{calendar.month_name[start.month]} {start.year}</h1>
	<div class="grid-calendar">
		<div class="row calendar-week-header">
			<div class="col grid-cell border"><div><div><span>Sunday</span></div></div></div>
			<div class="col grid-cell border"><div><div><span>Monday</span></div></div></div>
			<div class="col grid-cell border"><div><div><span>Tuesday</span></div></div></div>
			<div class="col grid-cell border"><div><div><span>Wednesday</span></div></div></div>
			<div class="col grid-cell border"><div><div><span>Thursday</span></div></div></div>
			<div class="col grid-cell border"><div><div><span>Friday</span></div></div></div>
			<div class="col grid-cell border"><div><div><span>Saturday</span></div></div></div>
		</div>"""
    found = False
    for i in range(0, 5):       
        html += '<div class="row calendar-week">'
        for j in range(0,7):
            # start adding date info when the first day of the week is found
            if not found:
                if (start.weekday() + 6) % 7 == j:
                    found = True
            dayNumber = ''
                
            html += f'<div class="col grid-cell border">'
            # start adding stuff when a day of the month is found
            if found:
                # only add day if within that month. Not adding days from previous and next month
                if start < end:
                    dayNumber = start.day
                    html += f"<div>{dayNumber}</div>"
                    entries_list = entries.get(start, [])
                    for entry in entries_list:
                        html += f'<a href="/entries/{entry.id}" class="btn btn-warning btn-sm d-block my-1">{entry.restaurant.name}<br><span class="badge bg-success">${round(entry.amount, 2):.2f}</span></a>'
                    
                start = start + datetime.timedelta(days=1)
            html += "</div>"
        html += '</div>'
    html += '</div>'
    return html

# returns dict for easy reference when adding to calendar
def get_entries_for_user(db, user_id, startdate, enddate):
    entries = Entry.query.filter(Entry.user_id==user_id, Entry.date.between(startdate, enddate)).all()
    entries_dict = {}
    
    for entry in entries:
        if not entries_dict.get(entry.date):
            entries_dict[entry.date] = []
        entries_dict[entry.date].append(entry)
    
    return entries_dict

def get_restaurant(db, name, yelp_id):
    restaurant = None
    # find restaurant by yelp_id
    if yelp_id:
        restaurant = Restaurant.query.filter_by(yelp_id=yelp_id).first()
        
        if restaurant and name != restaurant.name:
            # update the name in case it's different, for display purposes
            restaurant.name = name
            db.session.commit()
    
    # if restaurant not found and yelp_id not supplied, try finding by name
    if not restaurant and not yelp_id:
        restaurant = Restaurant.query.filter_by(name=name).first()
        
    # if still not found create a new restaurant
    if not restaurant:
        restaurant = register_restaurant(db, name=name, yelp_id=yelp_id)
    
    return restaurant

def register_restaurant(db, name, yelp_id):
    
    restaurant = Restaurant(name=name)
    if yelp_id:
        yelp_data = fetch_restaurant_from_yelp(yelp_id)
        
        yelp_id = yelp_data.get('id', None)
        img_url = yelp_data.get('image_url', None)
            
        restaurant.yelp_id = yelp_id
        restaurant.img_url = img_url
        
    db.session.add(restaurant)
    db.session.commit()
    
    return restaurant
        
def fetch_restaurant_from_yelp(yelp_id):
    load_dotenv()
    YELP_API_KEY = os.getenv('YELP_API_KEY')
    
    if not YELP_API_KEY:
        raise Exception('Missing API Key')

    url = f"https://api.yelp.com/v3/businesses/{yelp_id}"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {YELP_API_KEY}"
    }

    response = requests.get(url, headers=headers)
    
    if response.json().get('id', None):
        return response.json()
    else:
        if response.json().get('code') == 'Validation_ERROR':
            raise Exception('Bad API Key')
        raise Exception('Invalid Yelp ID')