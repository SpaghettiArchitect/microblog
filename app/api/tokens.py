from app import db
from app.api import bp
from app.api.auth import basic_auth


@bp.route("/tokens", methods=["POST"])
@basic_auth.login_required
def get_token() -> dict[str, str]:
    """Generate and return an authentication token for the authenticated user.

    Returns:
        token (dict[str, str]): A dictionary containing the authentication token.
    """
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return {"token": token}


def revoke_token():
    pass
