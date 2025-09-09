import sqlalchemy as sa
from flask_babel import _
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, ValidationError

from app import db
from app.models import User


class EditProfileForm(FlaskForm):
    """Form to update the profile information of a user."""

    username = StringField(_l("New username"), validators=[DataRequired()])
    about_me = TextAreaField(_l("About me"), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l("Update profile"))

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
                raise ValidationError(_("Please use a different username."))


class EmptyForm(FlaskForm):
    """An empty form with only a submit button. Useful for actions that
    require a POST request but no data from the user.
    """

    submit = SubmitField(_l("Submit"))


class PostForm(FlaskForm):
    """A simple form to create a new post."""

    post = TextAreaField(
        _l("Say something..."), validators=[DataRequired(), Length(min=1, max=140)]
    )
    submit = SubmitField(_l("Post"))
