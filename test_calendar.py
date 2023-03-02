import os

from models import db, User, Restaurant, Entry
from unittest import TestCase
from bs4 import BeautifulSoup
from flask_login import login_user, current_user, logout_user
import re
from datetime import date
from calendar import month_name
from eot_calendar.helpers import get_restaurant, fetch_restaurant_from_yelp, register_restaurant, get_entries_for_user

os.environ['DATABASE_URL'] = 'postgresql:///capstone1-test'

# must import after setting database
from app import app
app.config['WTF_CSRF_ENABLED'] = False

class CalendarTestCases(TestCase):
    
    def createUser(self, username, password):
        u = User.register(username, password)
        db.session.commit()
        return u
        
    def setUp(self) -> None:
        self.client = app.test_client()
        app.test_request_context().push()

        db.drop_all()
        db.create_all()
        
        self.u = self.createUser("user1", "password1")
        login_user(self.u)
        
        return super().setUp()
    
    def tearDown(self) -> None:
        db.session.rollback()
        db.session.remove()
        logout_user()
        
    def test_new_user_gets_empty_calendar(self):
        with self.client as c:
            resp = c.get("/calendar")
            soup = BeautifulSoup(str(resp.data), 'html.parser')

            self.assertIsNotNone(soup.find(class_="calendar-view"))
            self.assertIsNone(soup.find("a", {"href":re.compile('/entries/\\d+')}))
            
            # should show current month and year
            today = date.today()
            self.assertIsNotNone(soup.find(string=f'{month_name[today.month]} {today.year}'))
            
            visited = soup.find("div", string="Places Visited").find_next_siblings("p")[0].text
            self.assertEqual(visited, '0')
    
            spent = soup.find("div", string="Total Spent").find_next_siblings("p")[0].text
            self.assertEqual(spent, '$0.00')
            
    def test_calendar_login_required(self):
        logout_user()
        with self.client as c:
            resp = c.get("/calendar", follow_redirects=True)
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(string="Please log in to access this page."))
            
    def test_add_entry_page_loads(self):
        with self.client as c:
            resp = c.get("/entries")
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            
            self.assertIsNotNone(soup.find(string="Add an Entry"))
            self.assertIsNotNone(soup.find(id="date"))
            self.assertIsNotNone(soup.find(id="amount"))
            self.assertIsNotNone(soup.find(id="name"))
            self.assertIsNotNone(soup.find(id="location"))
            self.assertIsNotNone(soup.find(id="search-yelp"))
            self.assertIsNotNone(soup.find(id="yelp_id"))
            self.assertIsNotNone(soup.find("button", string="Add Entry"))
            
    def test_add_entry_page_login_required(self):
        logout_user()
        with self.client as c:
            resp = c.get("/entries", follow_redirects=True)
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(string="Please log in to access this page."))
            
    def test_add_entry(self):
        with self.client as c:
            resp = c.post("/entries", data={"date": "2023-02-25", "amount":"12", "name":"Safeway", "yelp_id":"AKgtlmi-WFJde2Vyk4yD1A"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            
            # should land on entry view
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(string="Safeway"))
            self.assertIsNotNone(soup.find(class_="fa-star"))
            self.assertIsNotNone(soup.find("a", string="Edit"))
            self.assertIsNotNone(soup.find("button", string="Delete"))
            self.assertIsNotNone(soup.find(string=re.compile("Gellert")))
            self.assertIsNotNone(soup.find(string="Feb 25, 2023"))
            self.assertIsNotNone(soup.find(string="$12.00"))
            
            # check calendar for entry
            resp = c.get("/calendar?month=2&year=2023")
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find("a", {"href":re.compile('/entries/\\d+')}))
            self.assertIsNotNone(soup.find(string="Safeway"))
            
            visited = soup.find("div", string="Places Visited").find_next_siblings("p")[0].text
            self.assertEqual(visited, '1')
    
            spent = soup.find("div", string="Total Spent").find_next_siblings("p")[0].text
            self.assertEqual(spent, '$12.00')
            
            # add second entry
            resp = c.post("/entries", data={"date": "2023-02-21", "amount":"10", "name":"McDonald's", "yelp_id":"W0fZbPacqcaSrNb_q9_Pqw"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            resp = c.get("/calendar?month=2&year=2023")
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            visited = soup.find("div", string="Places Visited").find_next_siblings("p")[0].text
            self.assertEqual(visited, '2')
    
            spent = soup.find("div", string="Total Spent").find_next_siblings("p")[0].text
            self.assertEqual(spent, '$22.00')
            
    def test_add_entry_login_required(self):
        logout_user()
        with self.client as c:
            resp = c.post("/entries", data={"date": "2023-02-25", "amount":"12", "name":"Safeway", "yelp_id":"AKgtlmi-WFJde2Vyk4yD1A"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(string="Please log in to access this page."))
            
    def test_change_calendar_date(self):
        with self.client as c:
            resp = c.get("/calendar?month=10&year=2020")
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(string="October 2020"))
            
    def test_entry_page(self):
        with self.client as c:
            resp = c.post("/entries", data={"date": "2023-02-25", "amount":"12", "name":"Safeway", "yelp_id":"AKgtlmi-WFJde2Vyk4yD1A"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            
            resp = c.get("/entries/1")
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            
            self.assertIsNotNone(soup.find(string="Safeway"))
            self.assertIsNotNone(soup.find(class_="fa-star"))
            self.assertIsNotNone(soup.find("a", string="Edit"))
            self.assertIsNotNone(soup.find("button", string="Delete"))
            self.assertIsNotNone(soup.find(string=re.compile("Gellert")))
            self.assertIsNotNone(soup.find(string="Feb 25, 2023"))
            self.assertIsNotNone(soup.find(string="$12.00"))
    
    def test_entry_page_login_required(self):
        with self.client as c:
            resp = c.post("/entries", data={"date": "2023-02-25", "amount":"12", "name":"Safeway", "yelp_id":"AKgtlmi-WFJde2Vyk4yD1A"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            logout_user()
            resp = c.get("/entries/1", follow_redirects=True)
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(string="Please log in to access this page."))
            
    def test_edit_entry_page_loads(self):
        with self.client as c:
            resp = c.post("/entries", data={"date": "2023-02-25", "amount":"12", "name":"Safeway", "yelp_id":"AKgtlmi-WFJde2Vyk4yD1A"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            
            resp = c.get("/entries/1/edit")
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            
            self.assertEqual(soup.find(id="date").get('value'), "2023-02-25")
            self.assertEqual(soup.find(id="amount").get('value'), "12.00")
            self.assertEqual(soup.find(id="name").get('value'), "Safeway")
            self.assertEqual(soup.find(id="yelp_id").get('value'), "AKgtlmi-WFJde2Vyk4yD1A")
            
    def test_edit_entry_page_login_required(self):
        with self.client as c:
            resp = c.post("/entries", data={"date": "2023-02-25", "amount":"12", "name":"Safeway", "yelp_id":"AKgtlmi-WFJde2Vyk4yD1A"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            logout_user()
            resp = c.get("/entries/1/edit", follow_redirects=True)
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(string="Please log in to access this page."))
            
    def test_edit_entry(self):
        with self.client as c:
            resp = c.post("/entries", data={"date": "2023-02-25", "amount":"12", "name":"Safeway", "yelp_id":"AKgtlmi-WFJde2Vyk4yD1A"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
        
            resp = c.post("/entries/1", data={"date": "2023-02-26", "amount":"12.01", "name":"Safeway", "yelp_id":"AKgtlmi-WFJde2Vyk4yD1A"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(string="Feb 26, 2023"))
            
            # check that amount is updated on calendar too
            resp = c.get("/calendar?month=2&year=2023")
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            spent = soup.find("div", string="Total Spent").find_next_siblings("p")[0].text
            self.assertEqual(spent, '$12.01')
            
    def test_edit_entry_login_required(self):
        with self.client as c:
            resp = c.post("/entries", data={"date": "2023-02-25", "amount":"12", "name":"Safeway", "yelp_id":"AKgtlmi-WFJde2Vyk4yD1A"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            logout_user()
            resp = c.post("/entries/1", data={"date": "2023-02-26", "amount":"12.01", "name":"Safeway", "yelp_id":"AKgtlmi-WFJde2Vyk4yD1A"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(string="Please log in to access this page."))
            
    def test_delete_entry(self):
        with self.client as c:
            resp = c.post("/entries", data={"date": "2023-02-25", "amount":"12", "name":"Safeway", "yelp_id":"AKgtlmi-WFJde2Vyk4yD1A"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            
            resp = c.post("/entries/1/delete", follow_redirects=True)
            
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            # should redirect to calendar view
            self.assertIsNotNone(soup.find(class_="calendar-view"))
            
    def test_delete_entry_login_required(self):
        with self.client as c:
            resp = c.post("/entries", data={"date": "2023-02-25", "amount":"12", "name":"Safeway", "yelp_id":"AKgtlmi-WFJde2Vyk4yD1A"}, content_type="application/x-www-form-urlencoded", follow_redirects=True)
            logout_user()
            resp = c.post("/entries/1/delete", follow_redirects=True)
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            self.assertIsNotNone(soup.find(string="Please log in to access this page."))
            
    def test_search_yelp_request(self):
        with self.client as c:
            resp = c.get("/yelp-search?term=Mcd&location=San%20Francisco,%20CA", follow_redirects=True)
            resp_json = resp.json
            self.assertGreater(len(resp_json), 0)
            
    def test_search_yelp_request_with_missing_params(self):
        with self.client as c:
            resp = c.get("/yelp-search")
            self.assertEqual(resp.status_code, 400)
            
class CalendarHelperTestCases(TestCase):    
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
        self.app_context.pop()
        
    def test_search_yelp(self):
        from eot_calendar.helpers import search_yelp
        result = search_yelp("Mcd", "San Francisco, CA")
        self.assertGreater(len(result), 0)
        first_result = result[0]
        self.assertIsNotNone(first_result["id"])
        self.assertIsNotNone(first_result["name"])
        self.assertIsNotNone(first_result["address"])
        
    def test_fetch_restaurant_from_yelp(self):
        result = fetch_restaurant_from_yelp(self.test_yelp_id)
        self.assertIsNotNone(result["id"])
        self.assertIsNotNone(result["name"])
        self.assertIsNotNone(result["image_url"])
        
    def test_register_restaurant(self):
        r = register_restaurant(db, 'McD', self.test_yelp_id)
        r2 = db.session.get(Restaurant, r.id)
        self.assertIsNotNone(r2)
        
    def test_register_restaurant_with_bad_yelp_id(self):
        with self.assertRaises(Exception) as ex:
            register_restaurant(db, 'McD', "abcd")
        
        self.assertEqual(str(ex.exception), "Invalid Yelp ID")
        
    def test_get_restaurant_by_yelp_id(self):
        r = register_restaurant(db, 'McD', self.test_yelp_id)
        r2 = get_restaurant(db, yelp_id=self.test_yelp_id)
        self.assertEqual(r.id, r2.id)
        
    def test_get_restaurant_by_name_and_yelp_id(self):
        r = register_restaurant(db, 'McDonalds', self.test_yelp_id)
        r2 = get_restaurant(db, name="McD", yelp_id=self.test_yelp_id)
        self.assertEqual(r.id, r2.id)
        
    def test_get_restaurant_by_name_and_no_yelp_id(self):
        r = register_restaurant(db, 'McD', self.test_yelp_id)
        r2 = get_restaurant(db, name="McD")
        # new restaurant should be created because no yelp id was supplied
        self.assertNotEqual(r.id, r2.id)
        
    def test_get_entries_for_user(self):
        r =register_restaurant(db, 'McD', self.test_yelp_id)
        new_entry = Entry(date="2023-02-25", user_id=self.u.id, restaurant_id=r.id, amount=10)
        db.session.add(new_entry)
        db.session.commit()
        
        r = register_restaurant(db, 'McD', self.test_yelp_id)
        new_entry = Entry(date="2023-02-25", user_id=self.u.id, restaurant_id=r.id, amount=12)
        db.session.add(new_entry)
        db.session.commit()
        
        entries = get_entries_for_user(self.u.id, "2023-02-25", "2023-02-26")
        
        entries_for_date = entries[date(2023, 2, 25)]
        self.assertEqual(len(entries_for_date), 2)
        self.assertEqual(entries_for_date[0].amount, 10)
        self.assertEqual(entries_for_date[1].amount, 12)
        self.assertIsNone(entries.get(date(2023, 2, 26)))