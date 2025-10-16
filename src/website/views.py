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
    query = select(Event)

    all_events = db.session.execute(query).scalars().all()

    query = select(Category)
    all_categories = db.session.execute(query).scalars().all()

    return render_template('index.html', events=all_events, categories=all_categories)

@main_bp.route('/category/<string:category_name>')
def view_category(category_name):
    query = select(Category.id).where(Category.name == category_name)
    category_id = db.session.execute(query).scalars().all()
    if(category_id):
        category_id = int(category_id[0])
    else:
        print(f"Failed to retreive id for {category_name} category")
        category_id = 9999999

    query = select(Event).where(Event.category_id == category_id)
    events = db.session.execute(query).scalars().all()

    if(not events):
        flash(f"No events found in category: {category_name}.", "info")

    return render_template('index.html', events=events, selected_category=category_name)

@main_bp.route('/event/<string:event_id>')
def view_event(event_id):
    query = (
        select(Event, Category.name.label('category_name'))
        .join(Category, Event.category_id == Category.id)
        .where(Event.id == event_id)
    )

    result = db.session.execute(query).first()

    if(not result):
        flash(f"No event found for id: {event_id}.", "error")
        return redirect(url_for('main.index'))

    event, category_name = result

    return render_template('EventDetailsPage.html', event=event, category_name=category_name)

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
                    file.save(os.path.join(uploads_folder, filename))
                    image_filenames.append(filename)
        
            event_image_filenames = ','.join(image_filenames)
            print(event_image_filenames)

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
@login_required
def bookings():
    user_bookings = Booking.query.all()
    print(user_bookings)
    return render_template('UserBookingHistory.html')

#Page that shows a given events details
@main_bp.route('/event')
@login_required
def eventdetails():
    return render_template('EventDetailsPage.html')

#Page that shows the events a user has created
@main_bp.route('/myevents')
def my_events():
    query = (
        #Select all events
        select(Event)
    )
    user_events = db.session.execute(query).scalars().all()
    return render_template('UserCreatedEvents.html', events=user_events)

# Editing user created events
@main_bp.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = db.session.get(Event, event_id)
    if event is None or event.creator_id != current_user.id:
        flash('You are not authorized to edit this event.', 'danger')
        return redirect(url_for('main.my_events'))

    form = EventForm(obj=event)  # populate form with existing event data
    if form.validate_on_submit():
        form.populate_obj(event)
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('main.my_events'))

    return render_template('EditEvent.html', form=form, event=event)

# Deleting user created events
@main_bp.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = db.session.get(Event, event_id)

    if event is None:
        flash("Event not found.", "warning")
        return redirect(url_for('main.my_events'))

    # Make sure the logged-in user is the event creator
    if event.organiser_id != current_user.id:
        flash("You are not authorized to delete this event.", "danger")
        return redirect(url_for('main.my_events'))

    try:
        db.session.delete(event)
        db.session.commit()
        flash("Event deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting event: {e}", "danger")

    return redirect(url_for('main.my_events'))