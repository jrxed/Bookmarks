from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, FileField
from wtforms.validators import InputRequired, Length, ValidationError, Email

from .user import User


class RegisterForm(FlaskForm):
    login = StringField(validators=[InputRequired(), Length(min=4, max=20)])

    username = StringField(validators=[Length(min=4, max=20)])

    email = EmailField(validators=[InputRequired(), Email()])

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])

    profile_pic = FileField('Profile picture')

    submit = SubmitField("Register")

    def validate_login(self, login):
        existing_user = User.query.filter_by(login=login.data).first()

        if existing_user:
            raise ValidationError("That login is already taken. Please choose a different one.")

    def validate_email(self, email):
        existing_user = User.query.filter_by(email=email.data).first()

        if existing_user:
            raise ValidationError("That email is already taken. Please choose a different one.")


class LoginForm(FlaskForm):
    login = StringField(validators=[InputRequired(), Length(min=4, max=20)])

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])

    submit = SubmitField("Log in")


class AddCardForm(FlaskForm):
    title = StringField(validators=[InputRequired(), Length(max=20)])

    link = StringField(validators=[InputRequired()])

    description = StringField(validators=[Length(max=200)])

    preview = FileField('Preview image')

    submit = SubmitField('Add bookmark')


class EditCardForm(FlaskForm):
    title = StringField(validators=[InputRequired(), Length(max=20)])

    link = StringField(validators=[InputRequired()])

    description = StringField(validators=[Length(max=200)])

    preview = FileField('Preview image')

    submit = SubmitField('Edit bookmark')

