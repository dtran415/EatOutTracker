from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, DateField, DecimalField, SelectField, IntegerField
from wtforms.validators import DataRequired, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'placeholder':'Username'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder':'Email'})
    remember_me = BooleanField('Remember Me')
    
class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'placeholder':'Username'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder':'Email'})
    
class AddEntryForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[Optional()], render_kw={'placeholder':'Amount'})
    name = StringField('Restaurant Name', validators=[DataRequired()], render_kw={'placeholder':'Restaurant Name'})
    yelp_id = StringField('Yelp ID', render_kw={'placeholder':'Yelp ID'})
    
class EditEntryForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    amount = DecimalField('Amount', render_kw={'placeholder':'Amount'})
    name = StringField('Restaurant Name', validators=[DataRequired()], render_kw={'placeholder':'Restaurant Name'})
    yelp_id = StringField('Yelp ID', render_kw={'placeholder':'Yelp ID'})
    
class CalendarMonthYearForm(FlaskForm):
    choices = [(1, 'January'),
               (2, 'February'),
               (3, 'March'),
               (4, 'April'),
               (5, 'May'),
               (6, 'June'),
               (7, 'July'),
               (8, 'August'),
               (9, 'September'),
               (10, 'October'),
               (11, 'November'),
               (12, 'December')]
    month = SelectField('Month', coerce=int, choices = choices )
    year = IntegerField('Year')
    
class ChartsDateRangeForm(FlaskForm):
    startdate = DateField('Date', validators=[DataRequired()])
    enddate = DateField('Date', validators=[DataRequired()])