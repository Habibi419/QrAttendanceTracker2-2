from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, NumberRange

class SessionForm(FlaskForm):
    """Form for creating a new session"""
    session_name = StringField('Session Name', 
                               validators=[DataRequired(), 
                                           Length(min=3, max=100, 
                                                 message="Session name must be between 3 and 100 characters")])
    duration_minutes = IntegerField('Duration (minutes)', 
                                  validators=[DataRequired(),
                                            NumberRange(min=1, max=120, 
                                                      message="Duration must be between 1 and 120 minutes")],
                                  default=5)
    submit = SubmitField('Generate QR Code')

class LoginForm(FlaskForm):
    """Admin login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """Admin registration form"""
    username = StringField('Username', validators=[DataRequired(),
                                                 Length(min=3, max=64,
                                                       message="Username must be between 3 and 64 characters")])
    password = PasswordField('Password', validators=[DataRequired(),
                                                   Length(min=8,
                                                         message="Password must be at least 8 characters")])
    password2 = PasswordField('Confirm Password', 
                             validators=[DataRequired(),
                                        EqualTo('password', message="Passwords must match")])
    submit = SubmitField('Register')

class AttendanceForm(FlaskForm):
    """Form for students to mark attendance"""
    student_id = StringField('Student ID', 
                            validators=[DataRequired(), 
                                       Length(min=3, max=20, 
                                             message="Student ID must be between 3 and 20 characters")])
    reg_number = StringField('Registration Number', 
                           validators=[DataRequired(), 
                                      Length(min=3, max=30, 
                                            message="Registration number must be between 3 and 30 characters")])
    name = StringField('Full Name', 
                      validators=[DataRequired(), 
                                 Length(min=3, max=100, 
                                       message="Name must be between 3 and 100 characters")])
    submit = SubmitField('Mark Attendance')
