"""
Contains all form code
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired

from module.utilities import ManageUser


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


    def validate_username(self, username):
        user = ManageUser().get_by_username(username.data)
        if user is not None:
            raise ValidationError('Please use a different username.')


    def validate_email(self, email):
        user = ManageUser().get_by_email(email.data)
        if user is not None:
            raise ValidationError('Please use a different email address.')


class UploadForm(FlaskForm):
    photo = FileField('Image', validators=[
        FileRequired()
    ])
    submit = SubmitField('Submit')