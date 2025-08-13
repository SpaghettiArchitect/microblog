from typing import Literal

from flask import render_template

from app import app, db


@app.errorhandler(404)
def not_found_error(error) -> tuple[str, Literal[404]]:
    """Render the 404 error page and set the status code of the
    response to 404.
    """
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error) -> tuple[str, Literal[500]]:
    """Render the 500 error page and set the status code of the
    response to 500.
    """
    db.session.rollback()  # Reset db session to a clean state.
    return render_template("500.html"), 500
