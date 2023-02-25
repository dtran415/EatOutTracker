import os

from models import db, User
from unittest import TestCase

os.environ['DATABASE_URL'] = 'postgresql:///capstone1-test'

# must import after setting database
from app import app

app.config['SQLALCHEMY_ECHO'] = False

class UserModelTestCase(TestCase):
    
    def setUp(self) -> None:
        db.drop_all()
        db.create_all()
        return super().setUp()
    
    def tearDown(self) -> None:
        db.session.rollback()
        
    def test_register_user_with_good_input(self):
        User.register("user1", "password1")
        db.session.commit()
        user = User.query.filter(User.username=="user1").first()
        self.assertIsNotNone(user)
        
    def test_register_user_with_too_long_username(self):
        User.register("averyveryverylongusername", "password1")
        with self.assertRaises(Exception):
            db.session.commit()
            
    def test_register_user_with_used_username(self):
        User.register("user1", "password1")
        db.session.commit()
        User.register("user1", "password1")
        with self.assertRaises(Exception):
            db.session.commit()
    
    def test_authenticate_with_good_creds(self):
        u = User.register("user1", "password1")
        db.session.commit()
        authenticatedUser = User.authenticate("user1", "password1")
        self.assertEqual(u, authenticatedUser)
        
    def test_authenticate_with_bad_creds(self):
        u = User.register("user1", "password1")
        db.session.commit()
        authenticatedUser = User.authenticate("user1", "password2")
        self.assertFalse(authenticatedUser)
        
    