import os

os.environ["DATABASE_URL"] = "sqlite://"

import unittest
from datetime import datetime, timedelta, timezone

from app import app, db
from app.models import Post, User


class UserModelCase(unittest.TestCase):
    """Tests for User model functionality."""

    def setUp(self):
        """Create the app context and the database."""
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Remove the app context and drop the database."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        """Check that passwords are hashed correctly."""
        u = User(username="susan", email="susan@example.com")
        u.set_password("cat")
        self.assertFalse(u.check_password("dog"))
        self.assertTrue(u.check_password("cat"))

    def test_avatar(self):
        """Check that the url for the avatar of the user is correct."""
        u = User(username="john", email="john@example.com")
        avatar_url = (
            "https://www.gravatar.com/avatar/"
            + "d4c74594d841139328695756648b6bd6"
            + "?d=retro&s=128"
        )
        self.assertEqual(u.avatar(128), avatar_url)

    def test_follow(self):
        """Check that following and unfollowing works correctly."""
        # Create two users.
        u1 = User(username="john", email="john@example.com")
        u2 = User(username="susan", email="susan@example.com")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        # Check that the users are not following anyone.
        following = db.session.scalars(u1.following.select()).all()
        followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(following, [])
        self.assertEqual(followers, [])

        # Make john follow susan, and check this works correctly.
        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 1)
        self.assertEqual(u2.followers_count(), 1)
        u1_following = db.session.scalars(u1.following.select()).all()
        u2_followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(u1_following[0].username, "susan")
        self.assertEqual(u2_followers[0].username, "john")

        # Check that unfollowing works correctly.
        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 0)
        self.assertEqual(u2.followers_count(), 0)

    def test_follow_posts(self):
        """Check that the posts of followed users are returned correctly."""
        # Create four users.
        u1 = User(username="jonh", email="john@example.com")
        u2 = User(username="susan", email="susan@example.com")
        u3 = User(username="mary", email="mary@example.com")
        u4 = User(username="david", email="david@example.com")
        db.session.add_all([u1, u2, u3, u4])

        # Create four posts.
        now = datetime.now(timezone.utc)
        p1 = Post(
            body="post from john",
            author=u1,
            timestamp=now + timedelta(seconds=1),
        )
        p2 = Post(
            body="post from susan",
            author=u2,
            timestamp=now + timedelta(seconds=4),
        )
        p3 = Post(
            body="post from mary",
            author=u3,
            timestamp=now + timedelta(seconds=3),
        )
        p4 = Post(
            body="post from david",
            author=u4,
            timestamp=now + timedelta(seconds=2),
        )
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # Set up the followers.
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # Check the following posts of each user.
        f1 = db.session.scalars(u1.following_posts()).all()
        f2 = db.session.scalars(u2.following_posts()).all()
        f3 = db.session.scalars(u3.following_posts()).all()
        f4 = db.session.scalars(u4.following_posts()).all()

        # Check the posts are returned in the correct order.
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == "__main__":
    unittest.main(verbosity=2)
