import sqlalchemy as sa
from flask_babel import _
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app import db
from app.models import User


class LoginForm(FlaskForm):
    """Form to log in a user already registered."""

    username = StringField(_l("Username"), validators=[DataRequired()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember_me = BooleanField(_l("Remember me"))
    submit = SubmitField(_l("Sign in"))


class RegistrationForm(FlaskForm):
    """Form to register a new user to the site."""

    username = StringField(_l("Username"), validators=[DataRequired()])
    email = EmailField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    password2 = PasswordField(
        _l("Confirm password"),
        validators=[
            DataRequired(),
            EqualTo("password", message=_l("Passwords must match.")),
        ],
    )
    submit = SubmitField(_l("Register"))

    def validate_username(self, username: str) -> None:
        """Checks that the username is not already in use.
        If is in use, raises a ValidationError.

        This method is called automatically by WTForms.
        """
        user = db.session.scalar(sa.select(User).where(User.username == username.data))

        if user is not None:
            raise ValidationError(_("Please use a different username."))

    def validate_email(self, email: str) -> None:
        """Checks that the email is not already in use.
        If is in use, raises a ValidationError.

        This method is called automatically by WTForms.
        """
        user = db.session.scalar(sa.select(User).where(User.email == email.data))

        if user is not None:
            raise ValidationError(_("Please use a different email address."))


class ResetPasswordRequestForm(FlaskForm):
    """Form to request a password reset."""

    email = EmailField(_l("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_l("Request password reset"))


class ResetPasswordForm(FlaskForm):
    """Form to reset the password."""

    password = PasswordField(_l("New password"), validators=[DataRequired()])
    password2 = PasswordField(
        _l("Confirm new password"),
        validators=[
            DataRequired(),
            EqualTo("password", message=_l("Passwords must match.")),
        ],
    )
    submit = SubmitField(_l("Reset password"))
