import os

from models import db, User
from unittest import TestCase
from bs4 import BeautifulSoup
from flask_login import login_user, current_user, logout_user

os.environ['DATABASE_URL'] = 'postgresql:///capstone1-test'

# must import after setting database
from app import app
app.config['WTF_CSRF_ENABLED'] = False

class AuthTestCase(TestCase):
    
    def createUser(self, username, password):
        u = User.register(username, password)
        db.session.commit()
        return u
        
    def setUp(self) -> None:
        self.client = app.test_client()
        app.test_request_context().push()
        
        db.drop_all()
        db.create_all()
        return super().setUp()
    
    def tearDown(self) -> None:
        db.session.rollback()
        db.session.remove()
        
    def test_login_page_loads(self):
        
        with self.client as c:
            resp = c.get("/login")
            
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(id="username"))
            self.assertIsNotNone(soup.find(id="password"))
            self.assertIsNotNone(soup.find(id="remember_me"))
            self.assertIsNotNone(soup.find("button", string="Log In"))
            
    def test_signup_page_loads(self):
        with self.client as c:
            resp = c.get("/signup")
            
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(id="username"))
            self.assertIsNotNone(soup.find(id="password"))
            self.assertIsNotNone(soup.find("button", string="Sign Up"))
            
    def test_signup(self):
         with self.client as c:
            resp = c.post("/signup", data={"username": "user1", "password":"password1"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(class_="calendar-view"))
            
    def test_signup_with_existing_user(self):
        User.register("user1", "password1")
        db.session.commit()
        
        with self.client as c:
            resp = c.post("/signup", data={"username": "user1", "password":"password1"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(string="Username already taken"))
            
    def test_login(self):
        User.register("user1", "password1")
        db.session.commit()
        
        with self.client as c:
            resp = c.post("/login", data={"username": "user1", "password":"password1"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(class_="calendar-view"))
            
    def test_root_goes_calendar_when_logged_in(self):
        u = User.register("user1", "password1")
        db.session.commit()
        login_user(u)
        
        with self.client as c:
            resp = c.get("/", follow_redirects=True)
            
            # make sure we're logged in and see calendar when going to root
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(class_="calendar-view"))
            
    def test_logout(self):
        login_user(self.createUser("user1", "password1"))
        self.assertTrue(current_user.is_authenticated)
        
        with self.client as c:
            resp = c.get("/logout", follow_redirects=True)
            
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            # redirects to login page
            self.assertIsNotNone(soup.find(id="username"))
            self.assertIsNotNone(soup.find(id="password"))
            self.assertFalse(current_user.is_authenticated)
            
    def test_profile_page_loads(self):
        login_user(self.createUser("user1", "password1"))
        
        with self.client as c:
            resp = c.get("/profile", follow_redirects=True)
            
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            # shows username
            self.assertIsNotNone(soup.find(string="user1"))
            self.assertIsNotNone(soup.find(id="default_location"))
            
    def test_update_profile(self):
        login_user(self.createUser("user1", "password1"))
        
        with self.client as c:
            resp = c.post("/profile", data={"default_location": "San Francisco, CA"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(string="Profile Updated"))
            self.assertEqual(soup.find(id="default_location").get('value'), "San Francisco, CA")
            
            # go back to profile and default_location should be updated
            resp = c.get("/profile", follow_redirects=True)
            
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertEqual(soup.find(id="default_location").get('value'), "San Francisco, CA")
            
    def test_profile_need_login(self):
        with self.client as c:
            resp = c.get("/profile", follow_redirects=True)
            
        soup = BeautifulSoup(str(resp.data), 'html.parser')
        self.assertIsNotNone(soup.find(string="Please log in to access this page."))
        self.assertIsNotNone(soup.find(id="username"))
        self.assertIsNotNone(soup.find(id="password"))