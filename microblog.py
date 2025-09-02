import sqlalchemy as sa
import sqlalchemy.orm as so

from app import (
    app,
    cli,  # noqa: F401
    db,
)
from app.models import Post, User


@app.shell_context_processor
def make_shell_context() -> dict:
    """Returns symbols that can be used in the shell context when running
    'flask shell'.
    """
    return {"sa": sa, "so": so, "db": db, "User": User, "Post": Post}
