from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email, EqualTo

# creates the login information
class LoginForm(FlaskForm):
    user_name=StringField("User Name", validators=[InputRequired('Enter user name')])
    password=PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

 # this is the registration form
class RegisterForm(FlaskForm):
    user_name=StringField("User Name", validators=[InputRequired()])
    email = StringField("Email Address", validators=[Email("Please enter a valid email")])
    # linking two fields - password should be equal to data entered in confirm
    password=PasswordField("Password", validators=[InputRequired(),
                  EqualTo('confirm', message="Passwords should match")])
    confirm = PasswordField("Confirm Password")

    # submit button
    submit = SubmitField("Register")

 # Event Creation Form
class EventForm(FlaskForm):
    event_title=StringField("User Name", validators=[InputRequired()])
    #category = #DROPDOWN ?? 
    #experience_level = dropdown
    event_description = TextAreaField("Description", validators=[InputRequired()])
    #event_start_datetime = 
    #event_end_datetime =
    #event_location = 
    venue_details = TextAreaField("Venue Details", validators=[InputRequired()])
    #ticket_price = number??
    #tickets_available = number??
    #img = FileField()
    #terms_conditions = Bool


    submit = SubmitField("Publish")