from app.api import bp


@bp.route("/users/<int:id>", methods=["GET"])
def get_user(id: int):
    """Return a user."""
    pass


@bp.route("/users", methods=["GET"])
def get_users():
    """Return the collection of all users."""
    pass


@bp.route("/users/<int:id>/followers", methods=["GET"])
def get_followers(id: int):
    """Return the followers of this user."""
    pass


@bp.route("/users/<int:id>/following", methods=["GET"])
def get_following(id: int):
    """Return the users this user is following."""
    pass


@bp.route("/users", methods=["POST"])
def create_user():
    """Register a new user account."""
    pass


@bp.route("/users/<int:id>", methods=["PUT"])
def update_user(id: int):
    """Modify a user."""
    pass
