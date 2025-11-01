from tracemalloc import start
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import User, Event, Review, Category, Booking
from .forms import EventForm, ReviewForm
from . import db
from werkzeug.utils import secure_filename
import os
from sqlalchemy import select, or_
from datetime import datetime


uploads_folder = os.path.join(os.getcwd(), 'website', 'static', 'uploads')


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    upcoming_events = Event.query.filter(Event.start_time >= datetime.utcnow()).order_by(Event.start_time).all()
    past_events = Event.query.filter(Event.start_time < datetime.utcnow()).order_by(Event.start_time.desc()).all()

    return render_template('index.html', upcoming_events=upcoming_events, past_events=past_events)

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

@main_bp.route('/event/<string:event_id>', methods=['GET', 'POST'])
def view_event(event_id):
    event = db.session.get(Event, event_id)

    if(not event):
        flash(f"No event found for id: {event_id}.", "error")
        return redirect(url_for('main.index'))
    

    form = ReviewForm()
    if(form.validate_on_submit()):
        try:
            if(not current_user.is_authenticated):
                flash("You must be logged in to post a review.", "warning")
                return redirect(url_for("auth.login"))
            
            #Check the user has not already left a review
            existing_review = Review.query.filter_by(user_id=current_user.id, event_id=event.id).first()
            if(existing_review):
                flash("You have already reviewed this event.", "warning")
            else:
                review = Review(
                    user_id=current_user.id,
                    event_id=event.id,
                    rating=form.rating.data,
                    comment=form.comment.data
                )
                db.session.add(review)
                db.session.commit()
                flash("Review posted successfully.", "success")
            return redirect(url_for('main.view_event', event_id=event.id))
        except Exception as e:
            db.session.rollback() # Undo any partial changes to the db
            flash("Failed to post review, error: " + str(e), "danger")

    elif(form.errors):
        flash("Failed to post the review. Please try again, Error: " + str(form.errors), "danger")

    reviews = Review.query.filter_by(event_id=event.id).order_by(Review.created_at.desc()).all()

    # dynamic display string for the event time range
    start = event.start_time
    end = event.end_time

    if start and end and start.date() == end.date():
        event_time_range = f"{start.strftime('%d %b %Y, %I:%M %p')} – {end.strftime('%I:%M %p')}"
    elif start and end:
        event_time_range = f"{start.strftime('%d %b %Y, %I:%M %p')} – {end.strftime('%d %b %Y, %I:%M %p')}"
    elif start:
        event_time_range = start.strftime('%d %b %Y, %I:%M %p')
    elif end:
        event_time_range = end.strftime('%d %b %Y, %I:%M %p')
    else:
        event_time_range = ""

    return render_template("EventDetailsPage.html", event=event, category_name=event.category_name, reviews=reviews, form=form, event_time_range=event_time_range)


@main_bp.route('/search')
def search():
    search_term = request.args.get('search','').strip()
    if(search_term):
        query = f"%{search_term}%"
        events = db.session.scalars(
            db.select(Event).where(
                or_(
                    Event.title.like(query),
                    Event.description.like(query),
                    Event.location.like(query)
                )
            )
        ).all()
        if(not events):
            flash(f"No events found for '{search_term}'.", "info")
        return render_template('index.html', events=events, search_query=search_term)
    else:
        return redirect(url_for('main.index'))
    

#Create a new event with the submitted info
@main_bp.route('/event/create', methods=['GET','POST']) # both get and post
@login_required
def create_event():   
    form = EventForm()
    form.event_category.choices = [(category.id, category.name) for category in Category.query.all()]
    
    if form.validate_on_submit():
        try:
            # Check for duplicate events
            existing_event = Event.query.filter_by(
                title=form.event_title.data.strip(),
                start_time=form.event_start_datetime.data,
                location=form.event_location.data.strip()
            ).first()

            if(existing_event):
                flash("An event with the same title, start time and location already exists!", "warning")
                return redirect(url_for('main.create_event'))
            

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
    user_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('UserBookingHistory.html', bookings=user_bookings, now=datetime.utcnow())


#Page that shows the events a user has created
@main_bp.route('/myevents')
@login_required
def my_events():
    user_events = Event.query.filter_by(organiser_id=current_user.id).order_by(Event.start_time.desc()).all()
    return render_template('UserCreatedEvents.html', events=user_events)

# Editing user created events
@main_bp.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = db.session.get(Event, event_id)
    if event is None or event.organiser_id != current_user.id:
        flash('You are not authorized to edit this event.', 'danger')
        return redirect(url_for('main.my_events'))

    form = EventForm()  

    categories = db.session.execute(select(Category)).scalars().all()
    form.event_category.choices = [(str(c.id), c.name) for c in categories]

    from wtforms.validators import Optional

    form.event_image.validators = [*[
        v for v in form.event_image.validators
        if(v.__class__.__name__ != 'FileRequired')
    ], Optional()]


    # populate form with existing event data
    if(request.method == 'GET'):
        form.event_title.data = event.title
        form.event_category.data = str(event.category_id)
        form.event_experience_level.data = event.experience_level
        form.event_description.data = event.description
        form.event_start_datetime.data = event.start_time
        form.event_end_datetime.data = event.end_time
        form.event_location.data = event.location
        form.venue_details.data = event.venue_details
        form.ticket_price.data = event.ticket_price
        form.number_of_tickets.data = event.number_of_tickets
        form.terms_conditions.data = True 

    if form.validate_on_submit():
        try:
            if(form.number_of_tickets.data < event.tickets_sold): #Make sure not to remove tickets that have been sold
                flash(f"You cannot remove tickets that have already been sold. Currently {event.tickets_sold} ticket(s) have been sold.","danger")
                return redirect(url_for('main.edit_event', event_id=event.id))
            
            event.title = form.event_title.data
            event.category_id = int(form.event_category.data)
            event.experience_level = form.event_experience_level.data
            event.description = form.event_description.data
            event.start_time = form.event_start_datetime.data
            event.end_time = form.event_end_datetime.data
            event.location = form.event_location.data
            event.venue_details = form.venue_details.data
            event.ticket_price = form.ticket_price.data
            event.number_of_tickets = form.number_of_tickets.data

            uploaded_files = request.files.getlist(form.event_image.name)
            if uploaded_files and uploaded_files[0].filename:
                filenames = []
                for file in uploaded_files:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(uploads_folder, filename)
                    file.save(filepath)
                    filenames.append(filename)
                event.images = ','.join(filenames)

            db.session.commit()
            flash("Event updated successfully!", "success")
            return redirect(url_for("main.view_event", event_id=event.id))


        except Exception as e:
            db.session.rollback()
            flash(f"Error updating event: {e}", "danger")
    
    else: 
        if(request.method == "POST"):
            flash(f"Edit event form error: {form.errors}","warning")
    

    return render_template('EditEvent.html', form=form, event=event)

# Cancel Event
@main_bp.route('/cancel_event/<int:event_id>', methods=['POST'])
@login_required
def cancel_event(event_id):
    event = db.session.get(Event, event_id)

    if(event is None):
        flash("Event not fount.", "warning")
        return redirect(url_for('main.my_events'))
    
    if(event.organiser_id != current_user.id):
        flash("You are not authorised to cancel this event.", "danger")
        return redirect(url_for("main.my_events"))
        
    try:
        event.cancelled = True
        db.session.commit()
        flash(f"Event '{event.title}' has been cancelled.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Error cancelling event: {e}", "danger")
    
    return redirect(url_for('main.my_events'))

# Deleting user created events
@main_bp.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = db.session.get(Event, event_id)

    if event is None:
        flash("Event not found.", "warning")
        return redirect(url_for('main.my_events'))
    
    if(event.tickets_sold > 0):
        flash("Cannot delete an event with booked tickets.", "warning")
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


@main_bp.route('/book/<int:event_id>', methods=['POST'])
@login_required
def book_event(event_id):
    #Get event to book tickets for
    event = Event.query.get_or_404(event_id)

    try:
        ticket_qty = int(request.form.get('ticket_qty', 1))
        total_cost = ticket_qty*event.ticket_price

        #Check event is active
        if(not event.status == "Open"):
            if(event.status == "Inactive"):
                flash("Unable to book tickets on an event that has already occoured.", "warning")
            if(event.status == "Sold Out"):
                flash("Unable to book tickets on an event that has sold out.", "warning")
            if(event.status == "Cancelled"):
                flash("Unable to book tickets on an event that has been cancelled.", "warning")
            else:
                flash(f"Unable to book tickets on an event with status: {event.status}", "warning")
            return redirect(url_for('main.view_event', event_id=event_id))

        #Check for ticket availablilty 
        if(ticket_qty > event.tickets_remaining):
            flash(f"Only {event.tickets_remaining} ticket(s) remaining, unable to purchase {ticket_qty} ticket(s).", "danger")
            return redirect(url_for('main.view_event', event_id=event_id))
    
        # create the booking
        booking = Booking(
            user_id=current_user.id,
            event_id=event_id,
            ticket_qty=ticket_qty,
            ticket_price=event.ticket_price,
            order_total=total_cost
        )

        db.session.add(booking)
        db.session.commit()

        flash(f"Successfully booked {ticket_qty} ticket(s) for ${total_cost}. Your order ID is #{booking.id}","success")
        return redirect(url_for('main.bookings'))

    except Exception as e:
        db.session.rollback()
        flash("Booking failed: "+str(e),"danger")
        return redirect(url_for('main.view_event', event_id=event_id))
    


