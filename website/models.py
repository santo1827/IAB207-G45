from . import db
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import CheckConstraint

class User(db.Model, UserMixin):
    __tablename__ = 'users' # good practice to specify table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    email = db.Column(db.String(100), index=True, nullable=False)
    phone = db.Column(db.Integer, nullable=False)
	#password is never stored in the DB, an encrypted password is stored
	# the storage should be at least 255 chars long
    password_hash = db.Column(db.String(255), nullable=False)
    # relation to call user.comments and comment.name
    reviews = db.relationship('Review', backref='user')

    # string print method
    def __repr__(self):
        return f"Name: {self.name}"

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    experience_level = db.Column(db.String(50), nullable=True)
    
    description = db.Column(db.Text, nullable=False)

    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    location = db.Column(db.String(255), nullable=False)
    venue_details = db.Column(db.Text)

    ticket_price = db.Column(db.Integer, default=0)
    number_of_tickets = db.Column(db.Integer, nullable=False)

    organiser_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    images = db.Column(db.String(1000))
    reviews = db.relationship('Review', backref='events')

	# string print method
    def __repr__(self):
        return f"Event: {self.title}"

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    ticket_qty = db.Column(db.Integer, nullable=False)
    ticket_price = db.Column(db.Integer, nullable=False)
    order_total = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # string print method
    def __repr__(self):
        return f"Booking: {self.id}"


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    rating = db.Column(db.Float, CheckConstraint('rating >= 1 AND rating <= 5'), nullable=False)
    comment = db.Column(db.String(400))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # string print method
    def __repr__(self):
        return f"Review: {self.id}"
    
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(400), nullable=False)
    icon = db.Column(db.String(400), nullable=False)

    # string print method
    def __repr__(self):
        return f"Category: {self.name}"
