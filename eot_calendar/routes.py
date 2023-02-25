from flask import Blueprint, render_template, request, abort, redirect, url_for
from models import db, Entry
from flask_login import login_required, current_user
from eot_calendar.helpers import generateCalendarHTML, get_restaurant, fetch_restaurant_from_yelp, search_yelp, get_star_ratings_html
from forms import AddEntryForm, EditEntryForm, CalendarMonthYearForm
from datetime import datetime, date
import calendar
from sqlalchemy.sql import func

eot_calendar = Blueprint('calendar', __name__)

@eot_calendar.route('/calendar')
@login_required
def calendar_page():
    year = request.args.get('year')
    month = request.args.get('month')
    today = datetime.now().date()
    if not year and not month:
        year = today.year
        month = today.month
        
    year = int(year)
    month = int(month)
    
    form = CalendarMonthYearForm(month=month, year=year)
    
    range = calendar.monthrange(year, month)
    startdate = date(year, month, 1)
    enddate = date(year, month, range[1])
    
    # get number of restaurants visited by a specific user in date range
    numPlaces = db.session.query(Entry).filter(Entry.user_id==current_user.id, Entry.date.between(startdate, enddate)).distinct(Entry.restaurant_id).count()
    
    # get total spent for user for month
    totalSpent = db.session.query(func.sum(Entry.amount)).filter(Entry.user_id==current_user.id, Entry.date.between(startdate, enddate)).first()[0]
    
    calendarHTML = generateCalendarHTML(db, current_user.id, year, month)
        
    if not calendarHTML:
        abort(400)
        
    return render_template('calendar.html', calendarHTML=calendarHTML, current_user=current_user, form=form, numPlaces=numPlaces, totalSpent=totalSpent)

@eot_calendar.route('/entries')
@login_required
def add_entry_page():
    form = AddEntryForm()
    
    # if supplying a date prepopulate date
    if request.args.get('date'):
        form.date.data = datetime.strptime(request.args.get('date'), '%Y-%m-%d').date()
        
    return render_template('entry_add.html', current_user=current_user, form=form)

@eot_calendar.route('/entries', methods=['POST'])
@login_required
def add_entry():
    form = AddEntryForm()
    
    if form.validate_on_submit():
        date = form.date.data
        amount = form.amount.data
        name = form.name.data
        yelp_id = form.yelp_id.data
        
        try:
            restaurant = get_restaurant(db, name, yelp_id)
            new_entry = Entry(date=date, amount=amount, restaurant_id=restaurant.id, user_id=current_user.id)
            db.session.add(new_entry)
            db.session.commit()
            return redirect(url_for('calendar.show_entry', entry_id=new_entry.id))
        except Exception as e:
            form.yelp_id.errors.append(str(e))        
        
    return render_template('entry_add.html', current_user=current_user, form=form)

@eot_calendar.route('/entries/<int:entry_id>')
@login_required
def show_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    restaurant = {'name':entry.restaurant.name}
    ratingsHTML = None
    
    yelp_id = entry.restaurant.yelp_id
    if yelp_id:
        response = fetch_restaurant_from_yelp(entry.restaurant.yelp_id)
        restaurant['img_url'] = response.get('image_url')
        restaurant['display_address'] = response.get('location').get('display_address')
        restaurant['phone'] = response.get('display_phone')
        restaurant['ratings'] = response.get('rating')
        restaurant['review_count'] = response.get('review_count')
        restaurant['url'] = response.get('url')
        ratingsHTML = get_star_ratings_html(restaurant['ratings'])
    
    return render_template('entry_show.html', current_user=current_user, restaurant=restaurant, entry=entry, ratingsHTML=ratingsHTML)

@eot_calendar.route('/entries/<int:entry_id>/edit')
@login_required
def edit_entry_page(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    
    if entry.user_id != current_user.id:
        abort(403)
    
    form = EditEntryForm(obj=entry)
    form.name.data = entry.restaurant.name
    form.yelp_id.data = entry.restaurant.yelp_id
    return render_template('entry_edit.html', current_user=current_user, form=form, entry_id=entry.id)

@eot_calendar.route('/entries/<int:entry_id>', methods=['POST'])
@login_required
def edit_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    
    if entry.user_id != current_user.id:
        abort(403)
    
    form = AddEntryForm()
    
    if form.validate_on_submit():
        entry.date = form.date.data
        entry.amount = form.amount.data
        entry.name = form.name.data
        entry.yelp_id = form.yelp_id.data
        
        try:
            restaurant = get_restaurant(db, entry.name, entry.yelp_id)
            entry.restaurant_id = restaurant.id
            db.session.commit()
            return redirect(url_for('calendar.show_entry', entry_id=entry.id))
        except Exception as e:
            form.yelp_id.errors.append(str(e))
        
    return render_template('entry_edit.html', current_user=current_user, form=form, entry_id=entry.id)

@eot_calendar.route('/entries/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    
    if entry.user_id != current_user.id:
        abort(403)
    db.session.delete(entry)
    db.session.commit()
    
    return redirect(url_for('calendar.calendar_page'))

@eot_calendar.route('/yelp-search')
def search_yelp_request():
    term = request.args.get('term')
    location = request.args.get('location')
    
    if not term or not location:
        return ("Please supply term and location", 400)
    
    try:
        return search_yelp(term, location)
    except Exception as e:
        return (str(e), 500)
    