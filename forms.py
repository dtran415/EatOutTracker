from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'placeholder':'Username'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder':'Email'})
    remember_me = BooleanField('Remember Me')
    
class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'placeholder':'Username'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder':'Email'})