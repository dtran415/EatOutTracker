from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, DateField, DecimalField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'placeholder':'Username'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder':'Email'})
    remember_me = BooleanField('Remember Me')
    
class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'placeholder':'Username'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder':'Email'})
    
class AddEntryForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    amount = DecimalField('Amount', render_kw={'placeholder':'Amount'})
    name = StringField('Restaurant Name', validators=[DataRequired()], render_kw={'placeholder':'Restaurant Name'})
    yelp_id = StringField('Yelp ID', render_kw={'placeholder':'Yelp ID'})
    
class EditEntryForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    amount = DecimalField('Amount', render_kw={'placeholder':'Amount'})
    name = StringField('Restaurant Name', validators=[DataRequired()], render_kw={'placeholder':'Restaurant Name'})
    yelp_id = StringField('Yelp ID', render_kw={'placeholder':'Yelp ID'})