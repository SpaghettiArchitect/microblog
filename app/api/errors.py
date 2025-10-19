from typing import Literal, Optional

from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES

from app.api import bp


def error_response(
    status_code: int, message: Optional[str] = None
) -> tuple[dict[str, str], int]:
    """
    Generate a standardized error response payload for API endpoints.

    Args:
        status_code (int): The HTTP status code representing the error.
        message (Optional[str], optional): An optional custom error message to include in the response.

    Returns:
        payload (tuple[dict[str, str], int]): A tuple containing the error payload dictionary and the HTTP status code.
    """
    payload = {"error": HTTP_STATUS_CODES.get(status_code, "Unknown error")}

    if message:
        payload["message"] = message

    return payload, status_code


def bad_request(message: str) -> tuple[dict[str, str], Literal[400]]:
    """Generate a 400 Bad Request error response. This is the most common error response."""
    return error_response(400, message)


@bp.errorhandler(HTTPException)
def handle_exception(e: HTTPException) -> tuple[dict[str, str], int]:
    """Handle HTTP exceptions by returning a standardized error response."""
    return error_response(e.code)
