from typing import Any

import sqlalchemy as sa
from flask import request

from app import db
from app.api import bp
from app.models import User


@bp.route("/users/<int:id>", methods=["GET"])
def get_user(id: int) -> dict[str, Any]:
    """Return a user as a dictionary if found, 404 error otherwise.

    Args:
        id (int): The ID of the user to retrieve.
    Returns:
        user (dict[str, Any]): A dictionary representation of the user.
    """
    return db.get_or_404(User, id).to_dict()


@bp.route("/users", methods=["GET"])
def get_users() -> dict[str, Any]:
    """Return the collection of all users in a paginated format.

    Returns:
        users (dict[str, Any]): A dictionary containing the paginated users.
    """
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    return User.to_collection_dict(sa.select(User), page, per_page, "api.get_users")


@bp.route("/users/<int:id>/followers", methods=["GET"])
def get_followers(id: int):
    """Return the followers of this user."""
    pass


@bp.route("/users/<int:id>/following", methods=["GET"])
def get_following(id: int):
    """Return the users this user is following."""
    pass


@bp.route("/users", methods=["POST"])
def create_user():
    """Register a new user account."""
    pass


@bp.route("/users/<int:id>", methods=["PUT"])
def update_user(id: int):
    """Modify a user."""
    pass
