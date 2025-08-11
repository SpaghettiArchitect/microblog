from datetime import datetime, timezone
from hashlib import md5
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


class User(UserMixin, db.Model):
    """Represents the User schema in the database.
    Each user is unique.
    """

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    posts: so.WriteOnlyMapped["Post"] = so.relationship(back_populates="author")

    def __repr__(self) -> str:
        """String representation of a User object."""
        return f"<User {self.username}>"

    def set_password(self, password: str) -> None:
        """Set the password_hash stored in this instance."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check that the password matches the hash previosly stored."""
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        """Get the URL for a unique profile picture for the user using
        the Gravatar service.
        """
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        request = f"{digest}?d=retro&s={size}"
        return f"https://www.gravatar.com/avatar/{request}"


class Post(db.Model):
    """Represents the schema of a Post made by a User."""

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates="posts")

    def __repr__(self) -> str:
        """String representation of a Post object."""
        return f"<Post {self.body}>"


@login.user_loader
def load_user(id: str) -> User | None:
    """Callback used by flask-login to reload a user object from the user
    ID stored in the session.

    Returns the corresponding User object or None if the user does not exist.
    """
    return db.session.get(User, int(id))
