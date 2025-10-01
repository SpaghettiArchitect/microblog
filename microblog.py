import sqlalchemy as sa
import sqlalchemy.orm as so

from app import (
    cli,  # noqa: F401
    create_app,
    db,
)
from app.models import Message, Notification, Post, User

app = create_app()


@app.shell_context_processor
def make_shell_context() -> dict:
    """Returns symbols that can be used in the shell context when running
    'flask shell'.
    """
    return {
        "sa": sa,
        "so": so,
        "db": db,
        "User": User,
        "Post": Post,
        "Message": Message,
        "Notification": Notification,
    }
