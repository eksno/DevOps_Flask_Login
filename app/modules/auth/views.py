from flask import Blueprint, redirect, request, render_template, url_for, session as user_session

from app import app, Session
from app.components import orm
from app.components.utils import apply_metrics, exception_str, encrypt_user_dict
from app.components.cipher import AESCipher


mod = Blueprint("auth", __name__, url_prefix="/auth")

cipher = AESCipher()


@apply_metrics(endpoint="/auth/signin")
@mod.route("/signin", methods=["POST", "GET"])
def signin():
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

                    encrypted_password = (
                        session.query(orm.Password)
                        .filter(orm.Password.user_id == user.id)
                        .all()
                    )

                    encrypted_password = str(encrypted_password[0].password)
                    
                    app.logger.debug(userdata["E-Mail"] + " - exists, attempting to sign in...")
                    app.logger.debug(
                        "User Data - ID: "
                        + str(user.id)
                        + " | E-Mail: "
                        + user.email
                        + " | Username: "
                        + user.username
                    )

                    if userdata["Password"] == cipher.decrypt(encrypted_password):
                        # Signin successfull
                        app.logger.debug(userdata["E-Mail"] + " - correct password")
                        
                        user_dict = {
                            "id": user.id,
                            "email": user.email,
                            "username": user.username,
                            "password": userdata["Password"],
                        }

                        user_session["user"] = encrypt_user_dict(user_dict)

                        return redirect(url_for("user.index"))
                    else:
                        # Signin unsuccessfull
                        app.logger.debug(userdata["E-Mail"] + " - wrong password")

                        return render_template(
                            "signin.html", message="Wrong password or e-mail."
                        )  # TODO: Give a better message telling the person its the wrong password
                else:
                    app.logger.debug(userdata["E-Mail"] + " does not exist.")

                    # User does not exist
                    return render_template(
                        "signin.html", message="User does not exist."
                    )  # TODO: Give a better message telling the person the user does not exists
        except Exception as e:
            app.logger.error("Signin by " + userdata["E-Mail"] + " failed. Traceback - " + exception_str(e))
            return render_template("error.html", error="Signin has failed: " + exception_str(e))
        finally:
            app.logger.debug("session closed")



    app.logger.debug("signin default operation")
    # Default operation
    return render_template("signin.html", message="Haven't signed up yet?")


@apply_metrics(endpoint="/auth/signup")
@mod.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        app.logger.debug("request method POST")
        userdata = request.form

        app.logger.debug(userdata["E-Mail"] + " creating new user...")

        # Add user

        encrypted_password = cipher.encrypt(userdata["Password"])
        encrypted_token = cipher.encrypt("123user_token")

        new_user = orm.User(email=userdata["E-Mail"], username=userdata["Username"])
        new_password = orm.Password(password=encrypted_password, user=new_user)
        new_user_token = orm.UserToken(token=encrypted_token, user=new_user)

        try: 
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
                    return render_template("signup.html")  # TODO: Give some message telling the person the user already exists

                # Add user
                session.add(new_user)
                session.add(new_password)
                session.add(new_user_token)

                # Get user data
                user = (
                    session.query(orm.User)
                    .filter(orm.User.email == userdata["E-Mail"])
                    .all()
                )[0]
                
                user_dict = {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "password": userdata["Password"],
                }

                user_session["user"] = encrypt_user_dict(user_dict)
                
                # redirect to user
                return redirect(url_for("user.index"))

                
        except Exception as e:
            app.logger.error("Signup by " + userdata["E-Mail"] + " failed. Traceback - " + exception_str(e))
            return render_template("error.html", error="Signup has failed: " + exception_str(e))
        finally:
            app.logger.debug("session closed")


    # Default operation
    return render_template("signup.html")
