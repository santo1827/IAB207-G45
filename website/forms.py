from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, SelectField, DateTimeLocalField, IntegerField, BooleanField
from wtforms.validators import InputRequired, Length, Email, EqualTo, NumberRange


# creates the login information
class LoginForm(FlaskForm):
    user_name=StringField("User Name", validators=[InputRequired('Enter user name')])
    password=PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

 # this is the registration form
class RegisterForm(FlaskForm):
    user_name=StringField("User Name", validators=[InputRequired()])
    phone = StringField("Phone Number", validators=[InputRequired()])
    email = StringField("Email Address", validators=[Email("Please enter a valid email")])
    # linking two fields - password should be equal to data entered in confirm
    password=PasswordField("Password", validators=[InputRequired(),
                  EqualTo('confirm', message="Passwords should match")])
    confirm = PasswordField("Confirm Password")

    # submit button
    submit = SubmitField("Register")

 # Event Creation Form
class EventForm(FlaskForm):
    event_title=StringField("Event Title *", render_kw={"placeholder" : "E.g., Morning Yoga at the Park", "class": "form-control"}, id="eventTitle", validators=[InputRequired()])
    event_category_options = [('Yoga', 'Yoga'),
                        ('Running', 'Running'),
                        ('Bodybuilding','Bodybuilding'),
                        ('Powerlifting','Powerlifting'),
                        ('Swiming','Swiming'),
                        ('Cycling','Cycling'),]
    #choices=event_category_options,
    event_category = SelectField("Category *",  id='EventCategory', validators=[InputRequired()], render_kw={"class": "form-select"})

    event_experience_options = [('', 'Choose...'),
                                ('Beginner Friendly','Beginner Friendly'),
                                ('Intermediate','Intermediate'),
                                ('Advanced','Advanced')]
    
    event_experience_level = SelectField("Experience Level", choices=event_experience_options, id='ExperienceLevel', render_kw={"class": "form-select"})


    event_description = TextAreaField("Description *", id='eventDetailsTextArea', validators=[InputRequired()], render_kw={"placeholder" : "What should participants expect? What to bring? Any notes…", "class": "form-control"})
    
    event_start_datetime = DateTimeLocalField("Start", format="%Y-%m-%dT%H:%M", id='startDate', validators=[InputRequired()], render_kw={"class": "form-control", "type": "datetime-local"})
    event_end_datetime = DateTimeLocalField("End", format="%Y-%m-%dT%H:%M", id='endDate', validators=[InputRequired()], render_kw={"class": "form-control", "type": "datetime-local"})
    
    event_location = StringField("Event Address *", render_kw={"placeholder" : "Start typing address… or pick from the map", "class": "form-control"}, id="eventAddress", validators=[InputRequired()])

    venue_details = TextAreaField("Venue Details", id='eventAddressDetails', render_kw={"placeholder" : "E.g. Level 2, Entrance near the Food Court", "class": "form-control"}, validators=[InputRequired()])
    
    ticket_price = IntegerField("", id="TicketPrice", validators=[InputRequired(), NumberRange(min=0)],
                                render_kw={"class": "form-control",
                                           "type": "number",
                                           "min": "0",
                                           "step": "1",
                                           "placeholder": "0"})
    
    number_of_tickets = IntegerField("Tickets Available *", id="NumberOfTickets", validators=[InputRequired(), NumberRange(min=0)],
                                render_kw={"class": "form-control",
                                           "type": "number",
                                           "min": "1",
                                           "step": "1",
                                           "placeholder": "e.g., 20"})

    event_image = FileField("Upload Cover Image(s)", id='eventImages', validators=[FileAllowed(['jpeg','jpg', 'png', 'webp'], FileRequired())],
                            render_kw={'class': 'form-control',
                                       'multiple': True})
    
    terms_conditions = BooleanField("I agree to the", id='agreeTos', validators=[InputRequired()], render_kw={'class': 'form-check-input'})


    submit = SubmitField("Publish", render_kw={'class': 'btn btn-primary'})