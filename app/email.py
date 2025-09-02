from threading import Thread

from flask import Flask, render_template
from flask_babel import _
from flask_mail import Message

from app import app, mail
from app.models import User


def send_async_email(app: Flask, msg: Message) -> None:
    """Send an email asynchronously to avoid blocking the main thread."""
    with app.app_context():
        mail.send(msg)


def send_email(
    subject: str,
    sender: str,
    recipients: list[str],
    text_body: str,
    html_body: str,
) -> None:
    """Send an async email with the given subject, sender, recipients, and body."""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user: User) -> None:
    """Send a password reset email to the user with a token."""
    token = user.get_reset_password_token()
    send_email(
        _("[Microblog] Reset Your Password"),
        sender=app.config["ADMINS"][0],
        recipients=[user.email],
        text_body=render_template(
            "email/reset_password.txt",
            user=user,
            token=token,
        ),
        html_body=render_template(
            "email/reset_password.html",
            user=user,
            token=token,
        ),
    )
