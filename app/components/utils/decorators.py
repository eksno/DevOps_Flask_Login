from functools import wraps
from flask import session as render_template, session as user_session

from app import app, Session
from app.components import orm
from app.components import cipher
from app.components.utils import exception_str, decrypt_user_dict
from app.components.cipher import AESCipher

cipher = AESCipher()


def get_signed_in(func):
    @wraps(func)
    def wrapper():
        try:
            with Session.begin() as session:
                # Get user dict
                user_dict = decrypt_user_dict(user_session["user"])

                # Get user data
                user = (
                    session.query(orm.User)
                    .filter(orm.User.email == user_dict["email"])
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

                    if user_dict["password"] == cipher.decrypt(encrypted_password):
                        # user_dict is valid
                        return func(user)

        except Exception as e:
            app.logger.error("Failed validating user, Traceback - " + exception_str(e))
            return render_template("error.html", error="Validation failed: " + exception_str(e))
        finally:
            app.logger.debug("session closed")
        
        func(False)
    return wrapper