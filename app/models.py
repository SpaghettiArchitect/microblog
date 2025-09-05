from datetime import datetime, timezone
from hashlib import md5
from time import time
from typing import Optional

import jwt
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, db, login

# Association table that links a user with another user, to create a
# follower-following many-to-many relationship.
followers = sa.Table(
    "followers",
    db.metadata,
    sa.Column(
        "follower_id",
        sa.Integer,
        sa.ForeignKey("user.id"),
        primary_key=True,
    ),
    sa.Column(
        "followed_id",
        sa.Integer,
        sa.ForeignKey("user.id"),
        primary_key=True,
    ),
)


class User(UserMixin, db.Model):
    """Represents the User schema in the database.
    Each user is unique.
    """

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    posts: so.WriteOnlyMapped["Post"] = so.relationship(back_populates="author")

    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    # Models a many-to-many relationship between the followers of a user
    # and the users followed by a user.
    following: so.WriteOnlyMapped["User"] = so.relationship(
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates="followers",
    )

    followers: so.WriteOnlyMapped["User"] = so.relationship(
        secondary=followers,
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates="following",
    )

    def __repr__(self) -> str:
        """String representation of a User object."""
        return f"<User {self.username}>"

    def set_password(self, password: str) -> None:
        """Set the password_hash stored in this instance."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check that the password matches the hash previosly stored."""
        return check_password_hash(self.password_hash, password)

    def avatar(self, size) -> str:
        """Get the URL for a unique profile picture for the user using
        the Gravatar service.
        """
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        request = f"{digest}?d=retro&s={size}"
        return f"https://www.gravatar.com/avatar/{request}"

    def follow(self, user: "User") -> None:
        """Follow the given user if not already following them."""
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user: "User") -> None:
        """Unfollow the given user if currently following them."""
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user: "User") -> bool:
        """Check if the current user is following the given user."""
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self) -> int | None:
        """Return the number of users following the current user."""
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery()
        )
        return db.session.scalar(query)

    def following_count(self) -> int | None:
        """Return the number of users the current user is following."""
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery()
        )
        return db.session.scalar(query)

    def following_posts(self) -> sa.Select["Post"]:
        """Returns all the posts, from newest to oldest, of all the users
        the current user is following.
        """
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(
                sa.or_(
                    Follower.id == self.id,
                    Author.id == self.id,
                )
            )
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )

    def get_reset_password_token(self, expires_in: int = 600) -> str:
        """Generates a JWT token that can be used to reset the password
        of the user. The token expires in `expires_in` seconds (default 10 min).
        """
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token: str) -> Optional["User"]:
        """Verifies the given JWT token and returns the corresponding user
        if the token is valid. If the token is invalid or expired, returns None.
        """
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])[
                "reset_password"
            ]
        except Exception:
            return

        return db.session.get(User, id)


class Post(db.Model):
    """Represents the schema of a Post made by a User."""

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates="posts")

    language: so.Mapped[Optional[str]] = so.mapped_column(sa.String(5))

    def __repr__(self) -> str:
        """String representation of a Post object."""
        return f"<Post {self.body}>"


@login.user_loader
def load_user(id: str) -> Optional[User]:
    """Callback used by flask-login to reload a user object from the user
    ID stored in the session.

    Returns the corresponding User object or None if the user does not exist.
    """
    return db.session.get(User, int(id))
