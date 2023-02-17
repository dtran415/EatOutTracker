from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    
    db.app = app
    app.app_context().push()
    db.init_app(app)
    
class User(UserMixin, db.Model):
    
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    
    @classmethod
    def register(cls, username, password):
        
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        user = cls(username=username,
                   password=hashed_utf8)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        user = User.query.filter(User.username==username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
        
        
class Restaurant(db.Model):
    __tablename__ = "restaurants"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    yelp_id = db.Column(db.Text)
    img_url = db.Column(db.Text, db.ForeignKey('restaurants.id'), nullable=False)

class Entry(db.Model):
    __tablename__ = "entries"
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    amount = db.Column(db.Float)
    
    tags = db.relationship('Tag', secondary='tags_entries')
    
class Tag(db.Model):
    __tablename__ = "tags"
    
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.Text, nullable=False)
    
class TagEntry(db.Model):
    """Mapping of a playlist to a song."""

    __tablename__ = "tags_entries"
    
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)
    entry_id = db.Column(db.Integer, db.ForeignKey('entries.id'), nullable=False)