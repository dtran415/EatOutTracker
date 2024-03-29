import datetime
import calendar
from models import Restaurant, Entry
import requests
import os
from flask import url_for

# return None if invalid year month
def generateCalendarHTML(user_id, year=None, month=None):
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
    previousMonth = start - datetime.timedelta(days=1)
    # end is already next month
    nextMonth = end
    entries = get_entries_for_user(user_id, start, end)
    
    html = f"""<div class="content pl-1 text-center">
	<h1><a class='float-start text-decoration-none text-dark' href='?year={previousMonth.year}&month={previousMonth.month}'>&lt;</a>{calendar.month_name[start.month]} {start.year}<a class='float-end text-decoration-none text-dark' href='?year={nextMonth.year}&month={nextMonth.month}'>&gt;</a></h1>
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
    while start < end:
        html += '<div class="row calendar-week">'
        for j in range(0,7):
            # start adding date info when the first day of the week is found
            if not found:
                if (j + 6) % 7 == start.weekday():
                    found = True
                
            html += f'<div class="col grid-cell border">'
            # start adding stuff when a day of the month is found
            if found:
                # only add day if within that month. Not adding days from previous and next month
                if start < end:
                    entries_list = entries.get(start, [])
                    html += get_day_html(start, entries_list)
                    
                start = start + datetime.timedelta(days=1)
            html += "</div>"
        html += '</div>'
    html += '</div>'
    return html

def get_day_html(day, entries_list):
    dayNumber = day.day
    html = f"<div class='text-start'>{dayNumber} <a class='btn btn-outline-success btn-sm float-end py-0 px-1' href='{url_for('calendar.add_entry_page', date=day.strftime('%Y-%m-%d'))}'>+</a></div>"
    for entry in entries_list:
        html += f'<a href="{url_for("calendar.show_entry", entry_id=entry.id)}" class="btn btn-warning btn-sm d-block my-1">{entry.restaurant.name}<br>'
        if entry.amount:
            html += f'<span class="badge bg-success">${round(entry.amount, 2):.2f}</span>'
        html += '</a>'
                        
    return html

# returns dict for easy reference when adding to calendar
def get_entries_for_user(user_id, startdate, enddate):
    entries = Entry.query.filter(Entry.user_id==user_id, Entry.date.between(startdate, enddate)).all()
    entries_dict = {}
    
    for entry in entries:
        if not entries_dict.get(entry.date):
            entries_dict[entry.date] = []
        entries_dict[entry.date].append(entry)
    
    return entries_dict

def get_restaurant(db, name=None, yelp_id=None):
    restaurant = None
    # find restaurant by yelp_id
    if yelp_id:
        restaurant = Restaurant.query.filter_by(yelp_id=yelp_id).first()
        
        if restaurant and name is not None and name != restaurant.name:
            # update the name in case it's different, for display purposes
            restaurant.name = name
            db.session.commit()
    
    # if restaurant not found and yelp_id not supplied, try finding by name
    if not restaurant and not yelp_id:
        restaurant = Restaurant.query.filter_by(name=name, yelp_id=None).first()
        
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
    YELP_API_KEY = os.environ.get('YELP_API_KEY')
    
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
    
def search_yelp(term, location):
    YELP_API_KEY = os.environ.get('YELP_API_KEY')
    
    if not YELP_API_KEY:
        raise Exception('Missing API Key')

    url = f"https://api.yelp.com/v3/businesses/search?location={location}&term={term}&sort_by=best_match&limit=20"


    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {YELP_API_KEY}"
    }

    response = requests.get(url, headers=headers)
    if response.json().get('error'):
        raise Exception(response.json().get('error').get('description'))
    
    results = []
    businesses = response.json().get("businesses")
    for business in businesses:
        displayAddress = "<br>".join(business.get("location").get("display_address"))
        results.append({
            "id":business.get("id"),
            "name":business.get("name"),
            "address":displayAddress
        })
    
    return results

def get_star_ratings_html(rating):
    html = '<span>'
    for i in range(5):
        diff = rating - i
        if diff >= 1:
            html += '<i class="fa-solid fa-star"></i>'
        elif diff >= 0:
            html += '<i class="fa-solid fa-star-half-stroke"></i>'
        else:
            html += '<i class="fa-regular fa-star"></i>'
    html += '</span>'
    return html