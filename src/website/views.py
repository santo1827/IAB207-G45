from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Event, Comment
#from .forms import EventForm
from . import db


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
        destinations = db.session.scalars(db.select(Destination).where(Destination.description.like(query)))
        return render_template('index.html', destinations=destinations)
    else:
        return redirect(url_for('main.index'))
    


@main_bp.route('/event/create', methods=['GET','POST']) # both get and post
#@login_required
def create_event():
     #if current_user.usertype != 'admin':
     #     flash("Need administrator login")
     #     return redirect(url_for('auth.login'))
     
     
     print('Creating Event')
     #form = EventForm()
     '''
     if form.validate_on_submit():
          print("Form has been submitted successfully")
          #Create a new event with the submitted info
          #new_event = Event(name=form.name.data, description=form.description.data,image=form.image.data)

          db.session.add(new_event)
          db.session.commit()
          return redirect(url_for('main.add_event'))'''
          
     return render_template('EventCreation.html')#, form=form)