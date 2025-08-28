import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    EmailField,
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from app import db
from app.models import User


class LoginForm(FlaskForm):
    """Form to log in a user already registered."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign in")


class RegistrationForm(FlaskForm):
    """Form to register a new user to the site."""

    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Confirm password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username: str) -> None:
        """Checks that the username is not already in use.
        If is in use, raises a ValidationError.

        This method is called automatically by WTForms.
        """
        user = db.session.scalar(sa.select(User).where(User.username == username.data))

        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email: str) -> None:
        """Checks that the email is not already in use.
        If is in use, raises a ValidationError.

        This method is called automatically by WTForms.
        """
        user = db.session.scalar(sa.select(User).where(User.email == email.data))

        if user is not None:
            raise ValidationError("Please use a different email address.")


class EditProfileForm(FlaskForm):
    """Form to update the profile information of a user."""

    username = StringField("New username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Update profile")

    def __init__(self, original_username: str, *args, **kwargs) -> None:
        """Creates an instance of this class and sets the original_username
        variable.
        """
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username: str) -> None:
        """Check that the new username is not already in use. If is in use,
        raise a ValidationError.
        """
        if username.data != self.original_username:
            user = db.session.scalar(
                sa.select(User).where(User.username == username.data)
            )
            if user is not None:
                raise ValidationError("Please use a different username.")


class EmptyForm(FlaskForm):
    """An empty form with only a submit button. Useful for actions that
    require a POST request but no data from the user.
    """

    submit = SubmitField("Submit")


class PostForm(FlaskForm):
    """A simple form to create a new post."""

    post = TextAreaField(
        "Say something...", validators=[DataRequired(), Length(min=1, max=140)]
    )
    submit = SubmitField("Post")


class ResetPasswordRequestForm(FlaskForm):
    """Form to request a password reset."""

    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request password reset")


class ResetPasswordForm(FlaskForm):
    """Form to reset the password."""

    password = PasswordField("New password", validators=[DataRequired()])
    password2 = PasswordField(
        "Confirm new password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset password")
