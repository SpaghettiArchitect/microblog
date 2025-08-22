from flask import render_template
from flask_mail import Message

from app import app, mail
from app.models import User


def send_email(
    subject: str,
    sender: str,
    recipients: list[str],
    text_body: str,
    html_body: str,
):
    """Send an email to a user or group of users with both plain text and
    HTML content."""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user: User):
    """Send a password reset email to the user with a token."""
    token = user.get_reset_password_token()
    send_email(
        "[Microblog] Reset Your Password",
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
