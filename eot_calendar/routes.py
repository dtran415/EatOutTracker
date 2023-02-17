from flask import Blueprint, render_template, request, abort
from models import db
from flask_login import login_required, current_user
from eot_calendar.helpers import generateCalendarHTML

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