from flask import Blueprint, render_template, redirect, url_for, flash
from forms import LoginForm, SignUpForm, ProfileUpdateForm
from models import db, User
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login_page():
    form = LoginForm()
    return render_template('login.html', current_user=None, form=form)

@auth.route('/signup')
def signup_page():
    form = SignUpForm()
    return render_template('signup.html', current_user=None, form=form)

@auth.route('/signup', methods=['POST'])
def signup():
    form = SignUpForm()
    
    if form.validate_on_submit():
        try:
            new_user = User.register(form.username.data, form.password.data)
            db.session.commit()
            login_user(new_user, remember=False)
            return redirect(url_for('calendar.calendar_page'))
        except IntegrityError:
            db.session.rollback()
            form.username.errors.append('Username already taken')
            
    return render_template('signup.html', form=form)

@auth.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        
        if user:
            rememberMe = form.remember_me.data
            login_user(user, remember=rememberMe)
            return redirect(url_for('calendar.calendar_page'))
        else:
            flash("Invalid Username/Password")
            
    return render_template('login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login_page'))

@auth.route('/profile')
@login_required
def profile_page():
    form = ProfileUpdateForm(default_location=current_user.default_location)
    return render_template('profile.html', user=current_user, form=form)

@auth.route('/profile', methods=['POST'])
@login_required
def update_profile():
    form = ProfileUpdateForm()
    
    if form.validate_on_submit():
        current_user.default_location = form.default_location.data
        db.session.commit()
        flash('Profile Updated')
        return redirect(url_for('auth.profile_page'))
    
    return render_template('profile.html', form=form)