from flask import Response, flash, redirect, render_template, url_for

from app import app
from app.forms import LoginForm


@app.route("/")
@app.route("/index")
def index() -> str:
    """Render the home page for Microblog."""
    # Mock objects to model some functionality of the site.
    user = {"username": "Spaghetti"}
    posts = [
        {
            "author": {"username": "John"},
            "body": "Beautiful day in Santiago!",
        },
        {
            "author": {"username": "Jane"},
            "body": "The Superman movie was so cool!",
        },
    ]

    return render_template(
        "index.html",
        title="Home",
        user=user,
        posts=posts,
    )


@app.route("/login", methods=["GET", "POST"])
def login() -> Response | str:
    """Render and validate the data on the login form."""
    form = LoginForm()

    if form.validate_on_submit():
        flash(
            f"Login requested for user {form.username.data}, remember_me={form.remember_me.data}"
        )
        return redirect(url_for("index"))

    return render_template("login.html", title="Sign In", form=form)
