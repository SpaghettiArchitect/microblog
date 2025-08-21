from datetime import datetime, timezone
from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import Response, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import app, db
from app.forms import EditProfileForm, EmptyForm, LoginForm, PostForm, RegistrationForm
from app.models import Post, User


@app.before_request
def before_request() -> None:
    """Callback function that is run before each new request is processed."""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index() -> str:
    """Render the home page for Microblog.

    This page contains the form to add a new post and shows the posts of all
    users the current user is following.
    """
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post is now live!")
        return redirect(url_for("index"))

    page = request.args.get("page", 1, type=int)
    posts = db.paginate(
        current_user.following_posts(),
        page=page,
        per_page=app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    next_url = url_for("index", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("index", page=posts.prev_num) if posts.has_prev else None

    return render_template(
        "index.html",
        title="Home Page",
        form=form,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@app.route("/login", methods=["GET", "POST"])
def login() -> Response | str:
    """Render and validate the data on the login form.

    If the data for the user and their password is correct, logs the user in.
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")

        return redirect(next_page)

    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout() -> Response:
    """Logs out the current user, and redirects to the index page."""
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register() -> Response | str:
    """Render and validate the data on the register form.

    If the data provided is valid, creates a new user in the database
    and redirects to the login page.
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))

    return render_template("register.html", title="Register", form=form)


@app.route("/user/<username>")
@login_required
def user(username: str) -> str:
    """Renders the user's profile page."""
    user = db.first_or_404(sa.select(User).where(User.username == username))
    form = EmptyForm()
    # Mock posts for now; delete after the functionality is implemented.
    posts = [
        {"author": user, "body": "Test post #1"},
        {"author": user, "body": "Test post #2"},
    ]

    return render_template("user.html", user=user, posts=posts, form=form)


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile() -> Response | str:
    """Render or process the form to edit the user's profile page."""
    form = EditProfileForm(current_user.username)

    # Saves the changes to the database if the form is correct.
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("edit_profile"))
    # Provides the initial version of the form pre-populated with the
    # information of the user.
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template("edit_profile.html", title="Edit Profile", form=form)


@app.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username: str) -> Response:
    """Make the current user follow another user."""
    form = EmptyForm()
    if form.validate_on_submit():
        # Check that the user to be followed exists and they aren't the current user.
        user = db.session.scalar(sa.select(User).where(User.username == username))
        if user is None:
            flash(f"User {username} not found.")
            return redirect(url_for("index"))
        if user == current_user:
            flash("You cannot follow yourself!")
            return redirect(url_for("user", username=username))

        # Make the current user follow the requested user.
        current_user.follow(user)
        db.session.commit()
        flash(f"You are now following {username}!")
        return redirect(url_for("user", username=username))
    else:
        return redirect(url_for("index"))


@app.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow(username: str) -> Response:
    """Make the current user unfollow another user."""
    form = EmptyForm()

    if form.validate_on_submit():
        # Check that the user to be unfollowed exists and they aren't the current user.
        user = db.session.scalar(sa.select(User).where(User.username == username))
        if user is None:
            flash(f"User {username} not found.")
            return redirect(url_for("index"))
        if user == current_user:
            flash("You cannot unfollow yourself!")
            return redirect(url_for("user", username=username))

        # Unfollow the requested user.
        current_user.unfollow(user)
        db.session.commit()
        flash(f"You stopped following {username}.")
        return redirect(url_for("user", username=username))
    else:
        return redirect(url_for("index"))


@app.route("/explore")
@login_required
def explore() -> str:
    """Render the page to explore all posts from all users."""
    page = request.args.get("page", 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(
        query,
        page=page,
        per_page=app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    next_url = url_for("explore", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("explore", page=posts.prev_num) if posts.has_prev else None

    return render_template(
        "index.html",
        title="Explore",
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
    )
