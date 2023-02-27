import os

from models import db, User, Entry
from unittest import TestCase
from bs4 import BeautifulSoup
from flask_login import login_user, logout_user
from eot_calendar.helpers import register_restaurant

os.environ['DATABASE_URL'] = 'postgresql:///capstone1-test'
# must import after setting database
from app import app
app.config['WTF_CSRF_ENABLED'] = False

class ChartTestCases(TestCase):
    
    def createUser(self, username, password):
        u = User.register(username, password)
        db.session.commit()
        return u
        
    def setUp(self) -> None:
        self.client = app.test_client()
        self.app_context = app.test_request_context()
        self.app_context.push()

        db.drop_all()
        db.create_all()
        
        self.u = self.createUser("user1", "password1")
        login_user(self.u)
        
        # McDonald's yelp ID
        self.test_yelp_id = "GqSDLvoiLDlWNb55T1tk5Q"
        
        return super().setUp()
    
    def tearDown(self) -> None:
        db.session.rollback()
        db.session.remove()
        logout_user()
        self.app_context.pop()
        
    def test_chart_page_loads_properly(self):
        with self.client as c:
            resp = c.get("/charts")
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            
            self.assertIsNotNone(soup.find(id="startdate"))
            self.assertIsNotNone(soup.find(id="enddate"))
            self.assertIsNotNone(soup.find(string="Places Visited"))
            self.assertIsNotNone(soup.find(string="Total Spent"))
            self.assertIsNotNone(soup.find(id="dailyExpenditure"))
            self.assertIsNotNone(soup.find(id="visits"))
            self.assertIsNotNone(soup.find(id="spent"))
            
    def test_fetch_chart_data(self):
        r =register_restaurant(db, 'McD', self.test_yelp_id)
        new_entry = Entry(date="2023-02-25", user_id=self.u.id, restaurant_id=r.id, amount=10)
        db.session.add(new_entry)
        db.session.commit()
        
        with self.client as c:
            resp = c.get("/charts/data")
            resp_json = resp.json
            
            self.assertIsNotNone(resp_json.get('daily'))
            self.assertIsNotNone(resp_json.get('spent'))
            self.assertIsNotNone(resp_json.get('visits'))
            self.assertEqual(resp_json.get('totalSpent'), 10)
            self.assertEqual(resp_json.get('numPlaces'), 1)