from flask import Blueprint, request, render_template

from app import app, Session, view_metric
from app.components import orm
from app.components.cipher import AESCipher


mod = Blueprint("auth", __name__, url_prefix="/auth")

cipher = AESCipher()


@mod.route("/signin", methods=["POST", "GET"])
def signin():
    view_metric.labels(endpoint="/signin").inc()
    app.logger.info("/signin loaded")

    if request.method == "POST":
        app.logger.debug("request method POST")
        userdata = request.form

        app.logger.debug(userdata["E-Mail"] + " login attempt...")

        # TODO: Add more bad data checks
        if len(userdata) != 2:
            app.logger.error("Data is bad")
            # Data is bad, return error
            return render_template("error.html", message="Bad Data")

        app.logger.debug("checking " + userdata["E-Mail"])

        app.logger.debug("creating and beginning database session...")
        with Session.begin() as session:
            app.logger.debug("session created and started")
            user = (
                session.query(orm.User)
                .filter(orm.User.email == userdata["E-Mail"])
                .all()
            )

            exists = len(user) is not 0

            if exists:
                user = {
                    "id": int(user[0].id),
                    "email": str(user[0].email),
                    "username": str(user[0].username),
                }

                encrypted_password = (
                    session.query(orm.Password)
                    .filter(orm.Password.user_id == user["id"])
                    .all()
                )

                encrypted_password = str(encrypted_password[0].password)

        app.logger.debug("session closed")

        app.logger.debug(exists)

        if not exists:
            app.logger.debug(userdata["E-Mail"] + " does not exist.")
            # User does not exist
            return render_template(
                "signin.html", message="User does not exist."
            )  # TODO: Give a better message telling the person the user already exists

        # User exists
        app.logger.debug(userdata["E-Mail"] + " does exist, signing in...")
        app.logger.debug(
            "User Data - ID: "
            + str(user["id"])
            + " | E-Mail: "
            + user["email"]
            + " | Username: "
            + user["username"]
        )

        if userdata["Password"] == cipher.decrypt(encrypted_password):
            app.logger.debug("sign in successfull")
            return render_template("signed_in.html", email=userdata["E-Mail"])
        app.logger.debug("sign in unsuccessful")

        return render_template(
            "signin.html", message="Wrong password or e-mail."
        )  # TODO: Give a better message telling the person the user already exists

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
            return render_template("error.html", message="Bad Data")

        # Add user

        encrypted_password = cipher.encrypt(userdata["Password"])
        user_token = cipher.encrypt("123user_token")

        new_user = orm.User(email=userdata["E-Mail"], username=userdata["Username"])
        new_password = orm.Password(password=encrypted_password, user=new_user)
        new_user_token = orm.UserToken(user_token=user_token, user=new_user)

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