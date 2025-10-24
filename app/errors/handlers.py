from typing import Literal, Union

from flask import render_template, request

from app import db
from app.api.errors import error_response as api_error_response
from app.errors import bp


def wants_json_response() -> bool:
    """Determine if the client prefers a JSON response over an
    HTML response based on the Accept header.

    Returns:
        bool: True if the client prefers JSON, False otherwise.
    """
    return (
        request.accept_mimetypes["application/json"]
        >= request.accept_mimetypes["text/html"]
    )


@bp.app_errorhandler(404)
def not_found_error(
    error,
) -> Union[tuple[dict[str, str], Literal[404]], tuple[str, Literal[404]]]:
    """Render the 404 error page and set the status code of the
    response to 404.

    Returns:
    - If the client accepts JSON responses, returns a JSON
    response with a 404 status code.
    - Otherwise, returns an HTML response rendering the 404
    error template with a 404 status code.
    """
    if wants_json_response():
        return api_error_response(404)
    return render_template("errors/404.html"), 404


@bp.app_errorhandler(500)
def internal_error(
    error,
) -> Union[tuple[dict[str, str], Literal[500]], tuple[str, Literal[500]]]:
    """Render the 500 error page and set the status code of the
    response to 500.

    Returns:
    - If the client accepts JSON responses, returns a JSON
    response with a 500 status code.
    - Otherwise, returns an HTML response rendering the 500
    error template with a 500 status code.
    """
    db.session.rollback()  # Reset db session to a clean state.
    if wants_json_response():
        return api_error_response(500)
    return render_template("errors/500.html"), 500
