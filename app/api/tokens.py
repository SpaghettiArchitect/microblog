from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth


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


@bp.route("/tokens", methods=["DELETE"])
@token_auth.login_required
def revoke_token():
    """Revoke the authentication token for the authenticated user.

    Returns:
        A `204 No Content` response indicating successful revocation.
    """
    token_auth.current_user().revoke_token()
    db.session.commit()
    return "", 204
