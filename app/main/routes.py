from datetime import datetime, timezone
from typing import Union

import sqlalchemy as sa
from flask import (
    Response,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_babel import _, get_locale
from flask_login import current_user, login_required
from langdetect import LangDetectException, detect

from app import db
from app.main import bp
from app.main.forms import (
    EditProfileForm,
    EmptyForm,
    MessageForm,
    PostForm,
    SearchForm,
)
from app.models import Message, Post, User
from app.translate import translate


@bp.before_request
def before_request() -> None:
    """Callback function that is run before each new request is processed."""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route("/translate", methods=["POST"])
@login_required
def translate_text() -> dict[str, str]:
    """Translate a text from a source language to a destination language."""
    data = request.get_json()
    return {"text": translate(data["text"], data["src_lang"], data["dest_lang"])}


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
@login_required
def index() -> str:
    """Render the home page for Microblog.

    This page contains the form to add a new post and shows the posts of all
    users the current user is following.
    """
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = ""
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_("Your post is now live!"))
        return redirect(url_for("main.index"))

    page = request.args.get("page", 1, type=int)
    posts = db.paginate(
        current_user.following_posts(),
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"],
        error_out=True,
    )
    next_url = url_for("main.index", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("main.index", page=posts.prev_num) if posts.has_prev else None

    return render_template(
        "index.html",
        title=_("Home"),
        form=form,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/user/<username>")
@login_required
def user(username: str) -> str:
    """Renders the user's profile page."""
    user: User = db.first_or_404(sa.select(User).where(User.username == username))

    # Implements the pagination of the user's posts.
    page = request.args.get("page", 1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(
        query,
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"],
        error_out=True,
    )
    next_url = (
        url_for("main.user", username=user.username, page=posts.next_num)
        if posts.has_next
        else None
    )
    prev_url = (
        url_for("main.user", username=user.username, page=posts.prev_num)
        if posts.has_prev
        else None
    )

    form = EmptyForm()  # Form to follow/unfollow the user.

    return render_template(
        "user.html",
        user=user,
        posts=posts.items,
        title=username,
        next_url=next_url,
        prev_url=prev_url,
        form=form,
    )


@bp.route("/user/<username>/popup")
@login_required
def user_popup(username: str) -> str:
    """Renders a small popup with the user's information."""
    user = db.first_or_404(sa.select(User).where(User.username == username))
    form = EmptyForm()
    return render_template("user_popup.html", user=user, form=form)


@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile() -> Union[Response, str]:
    """Render or process the form to edit the user's profile page."""
    form = EditProfileForm(current_user.username)

    # Saves the changes to the database if the form is correct.
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_("Your changes have been saved."))
        return redirect(url_for("main.user", username=current_user.username))
    # Provides the initial version of the form pre-populated with the
    # information of the user.
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template("edit_profile.html", title=_("Edit Profile"), form=form)


@bp.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username: str) -> Response:
    """Make the current user follow another user."""
    form = EmptyForm()
    if form.validate_on_submit():
        # Check that the user to be followed exists and they aren't the current user.
        user = db.session.scalar(sa.select(User).where(User.username == username))
        if user is None:
            flash(_("User %(username)s not found.", username=username))
            return redirect(url_for("main.index"))
        if user == current_user:
            flash(_("You cannot follow yourself!"))
            return redirect(url_for("main.user", username=username))

        # Make the current user follow the requested user.
        current_user.follow(user)
        db.session.commit()
        flash(_("You are now following %(username)s!", username=username))
        return redirect(url_for("main.user", username=username))
    else:
        return redirect(url_for("main.index"))


@bp.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow(username: str) -> Response:
    """Make the current user unfollow another user."""
    form = EmptyForm()

    if form.validate_on_submit():
        # Check that the user to be unfollowed exists and they aren't the current user.
        user = db.session.scalar(sa.select(User).where(User.username == username))
        if user is None:
            flash(_("User %(username)s not found.", username=username))
            return redirect(url_for("main.index"))
        if user == current_user:
            flash(_("You cannot unfollow yourself!"))
            return redirect(url_for("main.user", username=username))

        # Unfollow the requested user.
        current_user.unfollow(user)
        db.session.commit()
        flash(_("You stopped following %(username)s.", username=username))
        return redirect(url_for("main.user", username=username))
    else:
        return redirect(url_for("main.index"))


@bp.route("/explore")
@login_required
def explore() -> str:
    """Render the page to explore all posts from all users."""
    page = request.args.get("page", 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(
        query,
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"],
        error_out=True,
    )
    next_url = url_for("main.explore", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("main.explore", page=posts.prev_num) if posts.has_prev else None

    return render_template(
        "index.html",
        title=_("Explore"),
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/search")
@login_required
def search() -> Union[Response, str]:
    """Render the search results page."""
    if not g.search_form.validate():
        return redirect(url_for("main.explore"))

    page = request.args.get("page", 1, type=int)
    posts, total = Post.search(
        g.search_form.q.data,
        page,
        current_app.config["POSTS_PER_PAGE"],
    )
    next_url = (
        url_for("main.search", q=g.search_form.q.data, page=page + 1)
        if total > page * current_app.config["POSTS_PER_PAGE"]
        else None
    )
    prev_url = (
        url_for("main.search", q=g.search_form.q.data, page=page - 1)
        if page > 1
        else None
    )

    return render_template(
        "index.html",
        title=_("Search"),
        posts=posts,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/send_message/<recipient>", methods=["GET", "POST"])
@login_required
def send_message(recipient: str) -> Union[Response, str]:
    """Render or process the form to send a private message to another user."""
    user = db.first_or_404(sa.select(User).where(User.username == recipient))

    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash(_("Your message has been sent."))
        return redirect(url_for("main.user", username=recipient))

    return render_template(
        "send_message.html", title=_("Send message"), form=form, recipient=recipient
    )


@bp.route("/messages")
@login_required
def messages() -> str:
    """Render the page that shows the private messages received by the user."""
    # Mark all messages as read.
    current_user.last_message_read_time = datetime.now(timezone.utc)
    db.session.commit()

    # Get all the messages, and sort them from newest to oldest.
    page = request.args.get("page", 1, type=int)
    query = current_user.messages_received.select().order_by(Message.timestamp.desc())
    messages = db.paginate(
        query, page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=True
    )

    next_url = (
        url_for("main.messages", page=messages.next_num) if messages.has_next else None
    )
    prev_url = (
        url_for("main.messages", page=messages.prev_num) if messages.has_prev else None
    )

    return render_template(
        "messages.html",
        title=_("Messages"),
        messages=messages.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/preline.js")
def serve_preline_js() -> Response:
    """Serve the preline.js file from the node_modules directory."""
    return send_from_directory(
        current_app.config["PRELINE_JS_DIR"],
        "preline.js",
        mimetype="application/javascript",
    )
