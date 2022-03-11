from flask import Blueprint, request, render_template

from app import app, Session, view_metric
from app.components import orm
from app.components.utils import exception_str
from app.components.cipher import AESCipher


mod = Blueprint("auth", __name__, url_prefix="/auth")

cipher = AESCipher()


@mod.route("/signin", methods=["POST", "GET"])
def signin():
    view_metric.labels(endpoint="/signin").inc()
    app.logger.info("/signin loaded")

    if request.method == "POST":
        app.logger.debug("request method POST")
        
        # Get post data
        userdata = request.form

        app.logger.debug(userdata["E-Mail"] + " login attempt...")

        try:
            app.logger.debug("creating and beginning database session...")
            with Session.begin() as session:
                app.logger.debug("session created and started")

                # Get user data
                user = (
                    session.query(orm.User)
                    .filter(orm.User.email == userdata["E-Mail"])
                    .all()
                )

                exists = len(user) is not 0


                if exists:
                    # User exists
                    user = user[0]

                    user_dict = {
                        "id": int(user.id),
                        "email": str(user.email),
                        "username": str(user.username),
                    }

                    encrypted_password = (
                        session.query(orm.Password)
                        .filter(orm.Password.user_id == user_dict["id"])
                        .all()
                    )

                    encrypted_password = str(encrypted_password[0].password)
                    
                    app.logger.debug(userdata["E-Mail"] + " - exists, attempting to sign in...")
                    app.logger.debug(
                        "User Data - ID: "
                        + str(user_dict["id"])
                        + " | E-Mail: "
                        + user_dict["email"]
                        + " | Username: "
                        + user_dict["username"]
                    )

                    if userdata["Password"] == cipher.decrypt(encrypted_password):
                        # Signin successfull
                        app.logger.debug(userdata["E-Mail"] + " - correct password")

                        app.logger.debug(userdata["E-Mail"] + " - creating auth token...")
                        auth_token = user.encode_auth_token(user.id)
                        if auth_token and not isinstance(auth_token, Exception):
                            app.logger.debug("auth token created, redirecting... - " + auth_token)
                            return render_template("signed_in.html", email=userdata["E-Mail"], user_token=auth_token)
                        else:
                            app.logger.exception("signin failed" + exception_str(auth_token))
                            return render_template("error.html", error=exception_str(auth_token))
                    else:
                        # Signin unsuccessfull
                        app.logger.debug(userdata["E-Mail"] + " - wrong password")

                        return render_template(
                            "signin.html", message="Wrong password or e-mail."
                        )  # TODO: Give a better message telling the person the user already exists
                else:
                    app.logger.debug(userdata["E-Mail"] + " does not exist.")
                    # User does not exist
                    return render_template(
                        "signin.html", message="User does not exist."
                    )  # TODO: Give a better message telling the person the user already exists
        except Exception as e:
            app.logger.error("Signin by " + userdata["E-Mail"] + " failed. Traceback - " + exception_str(e))
            return render_template("error.html", error="Signin has failed: " + exception_str(e))
        finally:
            app.logger.debug("signin finished")



    app.logger.debug("default operation")
    # Default operation
    return render_template("signin.html", message="Haven't signed up yet?")


@mod.route("/signup", methods=["POST", "GET"])
def signup():
    view_metric.labels(endpoint="/signup").inc()
    app.logger.info("/signup loaded")

    if request.method == "POST":
        app.logger.debug("request method POST")
        userdata = request.form

        app.logger.debug(userdata["E-Mail"] + " creating new user...")

        # TODO: Add more bad data checks
        if len(userdata) != 3:
            app.logger.error("Data is bad")
            # Data is bad, return error
            return render_template("error.html", error="Bad Data")

        # Add user

        encrypted_password = cipher.encrypt(userdata["Password"])
        encrypted_token = cipher.encrypt("123user_token")

        new_user = orm.User(email=userdata["E-Mail"], username=userdata["Username"])
        new_password = orm.Password(password=encrypted_password, user=new_user)
        new_user_token = orm.UserToken(token=encrypted_token, user=new_user)

        app.logger.debug("creating and beginning database session...")
        with Session.begin() as session:
            app.logger.debug("session created and started")

            # Check if user exists
            if (
                session.query(orm.User)
                .filter(orm.User.email == userdata["E-Mail"])
                .scalar()
            ):
                app.logger.debug(userdata["E-Mail"] + " already exists...")
                return "signup.html"  # TODO: Give some message telling the person the user already exists

            # Add user
            session.add(new_user)
            session.add(new_password)
            session.add(new_user_token)
        app.logger.debug("session closed")

        # TODO: actually sign in.

        return render_template("redirect.html", url="/home")

    # Default operation
    return render_template("signup.html")
