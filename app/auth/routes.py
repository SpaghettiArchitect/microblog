from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import Response, flash, redirect, render_template, request, url_for
from flask_babel import _
from flask_login import current_user, login_user, logout_user

from app import db
from app.auth import bp
from app.auth.email import send_password_reset_email
from app.auth.forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
)
from app.models import User


@bp.route("/login", methods=["GET", "POST"])
def login() -> Response | str:
    """Render and validate the data on the login form.

    If the data for the user and their password is correct, logs the user in.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )

        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid username or password"))
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("main.index")

        return redirect(next_page)

    return render_template("auth/login.html", title=_("Sign In"), form=form)


@bp.route("/logout")
def logout() -> Response:
    """Logs out the current user, and redirects to the index page."""
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/register", methods=["GET", "POST"])
def register() -> Response | str:
    """Render and validate the data on the register form.

    If the data provided is valid, creates a new user in the database
    and redirects to the login page.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_("Congratulations, you are now a registered user!"))
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", title=_("Register"), form=form)


@bp.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request() -> Response | str:
    """Render the form to request a password reset."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash(_("Check your email for the instructions to reset your password."))
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/reset_password_request.html",
        title=_("Reset Password"),
        form=form,
    )


@bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token: str) -> Response | str:
    """Render the form to reset the password using a token sent by email."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("main.index"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_("Your password has been reset."))
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form)
