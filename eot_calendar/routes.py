from flask import Blueprint, render_template, request, abort, redirect, url_for
from models import db, Entry
from flask_login import login_required, current_user
from eot_calendar.helpers import generateCalendarHTML, get_restaurant
from forms import AddEntryForm

calendar = Blueprint('calendar', __name__)

@calendar.route('/calendar')
@login_required
def calendar_page():
    year = request.args.get('year')
    month = request.args.get('month')
    
    calendarHTML = None
    if year and month:
        calendarHTML = generateCalendarHTML(db, year, month)
    else:
        calendarHTML = generateCalendarHTML(db)
        
    if not calendarHTML:
        abort(400)
        
    return render_template('calendar.html', calendarHTML=calendarHTML, current_user=current_user)

@calendar.route('/entries')
@login_required
def entries_page():
    form = AddEntryForm()
    return render_template('entry_add.html', current_user=current_user, form=form)

@calendar.route('/entries', methods=['POST'])
@login_required
def add_entry():
    form = AddEntryForm()
    
    if form.validate_on_submit():
        date = form.date.data
        amount = form.amount.data
        name = form.name.data
        yelp_id = form.yelp_id.data
        
        restaurant = get_restaurant(db, name, yelp_id)
        new_entry = Entry(date=date, amount=amount, restaurant_id=restaurant.id, user_id=current_user.id)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('calendar.calendar_page'))
        
    return render_template('entry_add.html', current_user=current_user, form=form)

