from threading import Thread
from typing import List, Optional, Tuple

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
    recipients: List[str],
    text_body: str,
    html_body: str,
    attachments: Optional[List[Tuple]] = None,
    sync: bool = False,
) -> None:
    """
    Send an email with the given subject, sender, recipients, body, and attachments.

    Args:
        subject (str): Email subject.
        sender (str): Sender email address.
        recipients (List[str]): List of recipient email addresses.
        text_body (str): Plain text email body.
        html_body (str): HTML email body.
        attachments (List[Tuple], optional): List of attachment tuples, each in the format
            (filename, content_type, data).
        sync (bool, optional): If True, send the email synchronously (blocking the caller until sent);
            if False (default), send asynchronously in a background thread to avoid blocking.
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)

    if sync:
        mail.send(msg)
    else:
        Thread(
            target=send_async_email, args=(current_app._get_current_object(), msg)
        ).start()
