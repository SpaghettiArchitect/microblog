from flask import render_template

from app import app


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
