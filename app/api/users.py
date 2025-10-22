from typing import Any, Literal, Union

import sqlalchemy as sa
from flask import abort, request, url_for

from app import db
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
from app.models import User


@bp.route("/users/<int:id>", methods=["GET"])
@token_auth.login_required
def get_user(id: int) -> dict[str, Any]:
    """Return a user as a dictionary if found, 404 error otherwise.

    Args:
        id (int): The ID of the user to retrieve.
    Returns:
        user (dict[str, Any]): A dictionary representation of the user.
    """
    return db.get_or_404(User, id).to_dict()


@bp.route("/users", methods=["GET"])
@token_auth.login_required
def get_users() -> dict[str, Any]:
    """Return the collection of all users in a paginated format.

    Returns:
        users (dict[str, Any]): A dictionary containing the paginated users.
    """
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    return User.to_collection_dict(sa.select(User), page, per_page, "api.get_users")


@bp.route("/users/<int:id>/followers", methods=["GET"])
@token_auth.login_required
def get_followers(id: int):
    """Return the followers of a user.

    Args:
        id (int): The ID of the user whose followers are to be retrieved.
    Returns:
        followers (dict[str, Any]): A dictionary containing the paginated followers."""
    user = db.get_or_404(User, id)
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    return User.to_collection_dict(
        query=user.followers.select(),
        page=page,
        per_page=per_page,
        endpoint="api.get_followers",
        id=id,
    )


@bp.route("/users/<int:id>/following", methods=["GET"])
@token_auth.login_required
def get_following(id: int):
    """Return the users this user is following.

    Args:
        id (int): The ID of the user whose followings are to be retrieved.
    Returns:
        following (dict[str, Any]): A dictionary containing the paginated followings.
    """
    user = db.get_or_404(User, id)
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    return User.to_collection_dict(
        query=user.following.select(),
        page=page,
        per_page=per_page,
        endpoint="api.get_following",
        id=id,
    )


@bp.route("/users", methods=["POST"])
def create_user() -> Union[
    tuple[dict[str, str], Literal[400]], tuple[dict[str, Any], int, dict[str, str]]
]:
    """
    Create a new user from JSON request data. Validates that `username`, `email`, and `password` fields are present
    and that the `username` and `email` are unique.

    Returns:
    - On success, returns a tuple containing the user dictionary, HTTP status code 201, and Location header.
    - On failure, returns a tuple containing an error message dictionary and HTTP status code 400.
    """
    data = request.get_json()

    if "username" not in data or "email" not in data or "password" not in data:
        return bad_request("must include username, email and password fields")

    if db.session.scalar(sa.select(User).where(User.username == data["username"])):
        return bad_request("please use a different username")

    if db.session.scalar(sa.select(User).where(User.email == data["email"])):
        return bad_request("please use a different email address")

    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()

    return user.to_dict(), 201, {"Location": url_for("api.get_user", id=user.id)}


@bp.route("/users/<int:id>", methods=["PUT"])
@token_auth.login_required
def update_user(id: int) -> Union[tuple[dict[str, str], Literal[400]], dict[str, Any]]:
    """Modify a user. Validates that if `username` or `email` fields are being updated, they remain unique.

    Args:
        id (int): The ID of the user to update.

    Returns:
    - On success, returns the updated user dictionary.
    - On failure, returns a tuple containing an error message dictionary and HTTP status code 400.
    """
    # Ensure the authenticated user is the one being updated. A user can only update their own information.
    if token_auth.current_user().id != id:
        abort(403)

    user = db.get_or_404(User, id)
    data = request.get_json()

    if (
        "username" in data
        and data["username"] != user.username
        and db.session.scalar(
            sa.select(User).where(User.username == data["username"], User.id != id)
        )
    ):
        return bad_request("please use a different username")

    if (
        "email" in data
        and data["email"] != user.email
        and db.session.scalar(
            sa.select(User).where(User.email == data["email"], User.id != id)
        )
    ):
        return bad_request("please use a different email address")

    user.from_dict(data, new_user=False)
    db.session.commit()
    return user.to_dict()
