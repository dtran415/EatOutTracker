import datetime
import calendar

# return None if invalid year month
def generateCalendarHTML(db, year=None, month=None):
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
    print(start)
    print(end)
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
                
            html += f'<div class="col grid-cell border"><div>'
            # start adding stuff when a day of the month is found
            if found:
                # only add day if within that month. Not adding days from previous and next month
                if start < end:
                    dayNumber = start.day
                    html += f"<div>{dayNumber}</div>"
                    
                    # TODO Add events to day
                start = start + datetime.timedelta(days=1)
            html += "</div></div>"
        html += '</div>'
    html += '</div>'
    return html