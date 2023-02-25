from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from forms import ChartsDateRangeForm
from models import db, Entry, Restaurant
from datetime import datetime, date
from calendar import monthrange
from sqlalchemy.sql import func

eot_charts = Blueprint('eot_charts', __name__)

@eot_charts.route('/charts')
@login_required
def charts_page():
    startdate, enddate = get_start_and_end_date()
    form = ChartsDateRangeForm()
    form.startdate.data = startdate
    form.enddate.data = enddate
    return render_template('charts.html', form=form)

@eot_charts.route('/charts/data')
@login_required
def get_chart_data():
    startdate, enddate = get_start_and_end_date(request.args.get('startdate'), request.args.get('enddate'))
    
    # get all restaurants visited within a certain date range
    rows = db.session.query(Restaurant.name, func.count(Restaurant.name), func.sum(Entry.amount)).join(Entry).filter(Entry.user_id == current_user.id, Entry.date.between(startdate, enddate)).group_by(Restaurant.name).all()
    results = {'visits':[], 'spent':[], 'daily':{}}
    
    for row in rows:
        restaurant = row[0]
        visits = row[1]
        spent = round(row[2], 2)
        results['visits'].append({'restaurant':restaurant, 'visits':visits})
        results['spent'].append({'restaurant':restaurant, 'spent':spent})
        
    # get amount spent per day
    rows = db.session.query(Entry.date, func.sum(Entry.amount)).filter(Entry.user_id == current_user.id, Entry.date.between(startdate, enddate)).group_by(Entry.date).order_by(Entry.date.asc()).all()
    
    for row in rows:
        day = row[0].strftime('%Y/%m/%d')
        amount = round(row[1], 2)
        results['daily'][day] = amount
    
    return jsonify(results)
    
def get_start_and_end_date(startdate=None, enddate=None):
    today = datetime.now().date()
    range = monthrange(today.year, today.month)
    
    if not startdate and not enddate:
        startdate = date(today.year, today.month, 1)
        enddate = date(today.year, today.month, range[1])
    else:
        startdate = datetime.strptime(startdate, '%Y-%m-%d').date()
        enddate = datetime.strptime(enddate, '%Y-%m-%d').date()
        
    return startdate, enddate