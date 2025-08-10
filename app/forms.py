import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app import db
from app.models import User


class LoginForm(FlaskForm):
    """Render a simple login form."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    """Render a basic registration form."""

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username: str) -> None:
        """Checks that the username is not already in use.
        If is in use, raises a ValidationError.

        This method is called automatically by WTForms.
        """
        user = db.session.scalar(sa.select(User).where(User.username == username.data))

        if user is not None:
            raise ValidationError("Please use a different username")

    def validate_email(self, email: str) -> None:
        """Checks that the email is not already in use.
        If is in use, raises a ValidationError.

        This method is called automatically by WTForms.
        """
        user = db.session.scalar(sa.select(User).where(User.email == email.data))

        if user is not None:
            raise ValidationError("Please use a different email address.")
