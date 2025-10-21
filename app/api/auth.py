from typing import Optional

import sqlalchemy as sa
from flask_httpauth import HTTPBasicAuth

from app import db
from app.api.errors import error_response
from app.models import User

basic_auth = HTTPBasicAuth()


@basic_auth.verify_password
def verify_password(username: str, password: str) -> Optional[User]:
    """Verify user credentials for Basic HTTP Authentication.

    Args:
        username (str): The username provided by the client.
        password (str): The password provided by the client.

    Returns:
        user (User, None): The authenticated User object if credentials are valid, else None.
    """
    user = db.session.scalar(sa.select(User).where(User.username == username))

    if user and user.check_password(password):
        return user


@basic_auth.error_handler
def basic_auth_error(status: int) -> tuple[dict[str, str], int]:
    """Handle authentication errors for Basic HTTP Authentication.

    Args:
        status (int): The HTTP status code for the error.

    Returns:
        error (tuple[dict[str, str], int]): A tuple containing the error response dictionary and the status code.
    """
    return error_response(status)
