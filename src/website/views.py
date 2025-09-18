from flask import Blueprint, render_template, request, redirect, url_for
#from .models import Destination
from . import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    #destinations = db.session.scalars(db.select(Destination)).all()    
    return render_template('index.html')#, destinations=destinations)

@main_bp.route('/search')
def search():
    if request.args['search'] and request.args['search'] != "":
        print(request.args['search'])
        query = "%" + request.args['search'] + "%"
        destinations = db.session.scalars(db.select(Destination).where(Destination.description.like(query)))
        return render_template('index.html', destinations=destinations)
    else:
        return redirect(url_for('main.index'))