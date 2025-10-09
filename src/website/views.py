from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Event, Comment
from .forms import EventForm
from . import db
from werkzeug.utils import secure_filename
import os

uploads_folder = os.path.join(os.getcwd(), 'src', 'website', 'static', 'uploads')


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    events = Event.query.all() # Get all the events
    return render_template('index.html')#, events=events)

@main_bp.route('/search')
def search():
    if request.args['search'] and request.args['search'] != "":
        print(request.args['search'])
        query = "%" + request.args['search'] + "%"
        events = db.session.scalars(db.select(Event).where(Event.description.like(query)))
        return render_template('index.html', events=events)
    else:
        return redirect(url_for('main.index'))
    


@main_bp.route('/event/create', methods=['GET','POST']) # both get and post
@login_required
def create_event():
     #if current_user.usertype != 'admin':
     #     flash("Need administrator login")
     #     return redirect(url_for('auth.login'))
     
     
     print('Creating Event')
     form = EventForm()
     
     if form.validate_on_submit():
          print("Form has been submitted successfully")
          #Create a new event with the submitted info
          event_image_file = form.event_image.data
          event_image_filename = secure_filename(event_image_file.filename)
          filepath = os.path.join(uploads_folder, event_image_filename)
          event_image_file.save(filepath)

          new_event = Event(title=form.event_title.data,
                            category=form.event_category.data,
                            experience_level=form.event_experience_level.data,
                            description=form.event_description.data,
                            start_time=form.event_start_datetime.data,
                            end_time=form.event_end_datetime.data,
                            location=form.event_location.data,
                            venue_details=form.venue_details.data,
                            ticket_price=form.ticket_price.data,
                            number_of_tickets=form.number_of_tickets.data,
                            event_image=event_image_filename,
                            user_id=current_user.id)

          db.session.add(new_event)
          db.session.commit()
          return redirect(url_for('main.create_event'))
          
     return render_template('EventCreation.html', form=form)

@main_bp.route('/mybookings')
def bookings():
    return render_template('UserBookingHistory.html')

@main_bp.route('/eventdetails')
def eventdetails():
    return render_template('EventDetailsPage.html')

@main_bp.route('/user')
def user():
    return render_template('user.html')