from flask import Blueprint, session as user_session, render_template, redirect, url_for

from app import app, Session, view_metric
from app.components import orm
from app.components.utils import exception_str, get_user, apply_metrics
from app.components.cipher import AESCipher


mod = Blueprint("user", __name__, url_prefix="/user")

cipher = AESCipher()

@apply_metrics(endpoint="/user/")
@mod.route("/")
@get_user
def index(user):
    if user is False:
        return redirect(url_for("auth.signin"))
    
    app.logger.debug(user.email + " - creating auth token...")
    auth_token = user.encode_auth_token(user.id)
    if auth_token and not isinstance(auth_token, Exception):
        app.logger.debug("auth token created" + auth_token)

        return render_template("user.html", email=user.email, auth_token=auth_token)
    else:
        app.logger.exception("auth token creation failed" + exception_str(auth_token))
        return render_template("error.html", error=exception_str(auth_token))
