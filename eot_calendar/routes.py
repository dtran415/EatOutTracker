from flask import Blueprint, render_template, request, abort, redirect, url_for
from models import db, Entry
from flask_login import login_required, current_user
from eot_calendar.helpers import generateCalendarHTML, get_restaurant, fetch_restaurant_from_yelp
from forms import AddEntryForm

calendar = Blueprint('calendar', __name__)

@calendar.route('/calendar')
@login_required
def calendar_page():
    year = request.args.get('year')
    month = request.args.get('month')
    
    calendarHTML = None
    if year and month:
        calendarHTML = generateCalendarHTML(db, current_user.id, year, month)
    else:
        calendarHTML = generateCalendarHTML(db, current_user.id)
        
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
        
        try:
            restaurant = get_restaurant(db, name, yelp_id)
        except Exception as e:
            form.yelp_id.errors.append(str(e))
            return render_template('entry_add.html', current_user=current_user, form=form)
        new_entry = Entry(date=date, amount=amount, restaurant_id=restaurant.id, user_id=current_user.id)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('calendar.calendar_page'))
        
    return render_template('entry_add.html', current_user=current_user, form=form)

@calendar.route('/entries/<int:entry_id>')
@login_required
def show_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    restaurant = {'name':entry.restaurant.name}
    
    yelp_id = entry.restaurant.yelp_id
    if yelp_id:
        response = fetch_restaurant_from_yelp(entry.restaurant.yelp_id)
        restaurant['img_url'] = response.get('image_url')
        restaurant['display_address'] = response.get('location').get('display_address')
    
    
    return render_template('entry_show.html', current_user=current_user, restaurant=restaurant, entry=entry)