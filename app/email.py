from threading import Thread

from flask import Flask, current_app
from flask_mail import Message

from app import mail


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
    Thread(
        target=send_async_email, args=(current_app._get_current_object(), msg)
    ).start()
