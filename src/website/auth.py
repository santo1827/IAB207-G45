from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User
from .forms import LoginForm, RegisterForm
from . import db
#create a blueprint
auth_bp = Blueprint('auth', __name__ )

#=======================#
#--------Sign Up--------#
#=======================#
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()

    # Validate when user actually submits the form
    if request.method == 'POST' and register_form.validate_on_submit():
        uname = register_form.user_name.data
        pwd = register_form.password.data
        email = register_form.email.data
        phone = register_form.phone.data

        # Check if username already exists
        user = db.session.scalar(db.select(User).where(User.name == uname))
        if user:
            flash('Username already exists. Please choose another.', 'warning')
            return redirect(url_for('auth.register'))

        # Hash password for security
        pwd_hash = generate_password_hash(pwd)

        # Create new user
        new_user = User(
            name=uname,
            phone=phone,
            email=email,
            password_hash=pwd_hash
        )
        db.session.add(new_user)
        db.session.commit()

        # Success feedback
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('SignUp.html', form=register_form, heading='Register')



#=======================#
#--------Log In---------#
#=======================#
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    error = None

    # Process login logic when the user submits the form (POST)
    if request.method == 'POST' and login_form.validate_on_submit():
        user_name = login_form.user_name.data
        password = login_form.password.data

        # Find user by username
        user = db.session.scalar(db.select(User).where(User.name == user_name))

        # Validate credentials
        if user is None:
            error = 'Incorrect username'
        elif not check_password_hash(user.password_hash, password):
            error = 'Incorrect password'

        # Login if OK, otherwise flash the error
        if error is None:
            login_user(user)
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for('main.index'))
        else:
            flash(error, "warning")

    return render_template('LogIn.html', form=login_form, heading='Log In')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))