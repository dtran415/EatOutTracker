from flask import Flask, redirect, url_for
from eot_calendar.routes import eot_calendar
from auth.routes import auth
from eot_charts.routes import eot_charts
from models import connect_db, db, User
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///capstone1'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', default='secretkey')

connect_db(app)
db.create_all()

app.register_blueprint(auth)
app.register_blueprint(eot_calendar)
app.register_blueprint(eot_charts)

login_manager = LoginManager()
login_manager.login_view = 'auth.login_page'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('calendar.calendar_page'))
    return redirect(url_for('auth.login_page'))