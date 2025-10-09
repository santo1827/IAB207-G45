from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import User, Event, Review, Category, Booking
from .forms import EventForm
from . import db
from werkzeug.utils import secure_filename
import os
from sqlalchemy import select

uploads_folder = os.path.join(os.getcwd(), 'src', 'website', 'static', 'uploads')


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    #events = Event.query.all() # Get all the events
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
    form.event_category.choices = [(category.id, category.name) for category in Category.query.all()]
    
    if form.validate_on_submit():
        try:
            print("Success")
            #Create a new event with the submitted info

            # Get all uploaded images
            uploaded_images = request.files.getlist(form.event_image.name)
            image_filenames = []

            for file in uploaded_images:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(uploads_folder, filename)
                    file.save(filepath)
                    image_filenames.append(filename)
        
            event_image_filenames = ','.join(image_filenames)

            new_event = Event(title=form.event_title.data,
                            category_id=form.event_category.data,
                            experience_level=form.event_experience_level.data,
                            description=form.event_description.data,
                            start_time=form.event_start_datetime.data,
                            end_time=form.event_end_datetime.data,
                            location=form.event_location.data,
                            venue_details=form.venue_details.data,
                            ticket_price=form.ticket_price.data,
                            number_of_tickets=form.number_of_tickets.data,
                            images=event_image_filenames,
                            organiser_id=current_user.id)

            db.session.add(new_event)
            db.session.commit()

            print("Success")
            flash("Event created successfully!","success")
            
            return redirect(url_for('main.create_event'))
    

        except Exception as e:
            db.session.rollback() # Undo any partial changes to the db
            print(e)
            flash("Failed to create the event. Please try again, Error: " + str(e), "danger")
    elif(form.errors):
        flash("Failed to create the event. Please try again, Error: " + str(form.errors), "danger")
        print("Form Error:", form.errors)   
        
    return render_template('EventCreation.html', form=form)

# Page displaying the users booking
@main_bp.route('/mybookings')
def bookings():
    user_bookings = Booking.query.all()
    print(user_bookings)
    return render_template('UserBookingHistory.html')

#Page that shows a given events details
@main_bp.route('/event')
def eventdetails():
    return render_template('EventDetailsPage.html')

#Page that shows the events a user has created
@main_bp.route('/myevents')
def my_events():
    query = (
        #Select all events
        select(Event)

        .where(Event.organiser_id == 1)
    )
    user_events = db.session.execute(query).scalars().all()

    return render_template('UserCreatedEvents.html', events=user_events)