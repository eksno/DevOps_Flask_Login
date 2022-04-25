from flask import Blueprint, jsonify, render_template

from app import app, Session, load_duration_metric
from app.components import orm
from app.components.utils import apply_metrics, exception_str
from app.components.cipher import AESCipher
from app.components.utils.decorators import require_auth_token


mod = Blueprint("api", __name__, url_prefix="/api")

cipher = AESCipher()

@apply_metrics(endpoint="/api")
@mod.route("/")
def index():
    pass

@apply_metrics(endpoint="/api/users")
@mod.route("/users", methods=["POST", "GET"])
@load_duration_metric.time()
@require_auth_token
def users():
    try:
        app.logger.debug("creating and beginning database session...")
        with Session.begin() as session:
            app.logger.debug("session created and started")

            user_schema = orm.UserSchema()
            user_table = session.query(orm.User).all()
            user_dict = user_schema.dump(user_table)

            return jsonify(user_dict)

    except Exception as e:
        app.logger.error("/api/users failed. Traceback - " + exception_str(e))
        return render_template("error.html", error="Signin has failed: " + exception_str(e))
    finally:
        app.logger.debug("session closed")
