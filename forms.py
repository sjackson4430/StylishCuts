from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateTimeField, TextAreaField, SelectField, FloatField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class AppointmentForm(FlaskForm):
    client_name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    client_email = StringField('Email', validators=[DataRequired(), Email()])
    service = SelectField('Service', validators=[DataRequired()])
    date = DateTimeField('Date and Time', validators=[DataRequired()], format='%Y-%m-%d %H:%M')

class DealForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    valid_until = DateTimeField('Valid Until', validators=[DataRequired()], format='%Y-%m-%d')

class ServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    price = FloatField('Price', validators=[DataRequired()])
    duration = SelectField('Duration (minutes)', 
                         choices=[(30, '30'), (45, '45'), (60, '60')],
                         coerce=int,
                         validators=[DataRequired()])
