from functools import wraps
from textwrap import wrap
from flask import request, render_template, session as user_session, abort

from app import app, view_metric, Session
from app.components import orm
from app.components import cipher
from app.components.utils import exception_str, decrypt_user_dict
from app.components.cipher import AESCipher

cipher = AESCipher()

"""
Basic Decorator Template:

def basic_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        log_string = basic_decorator.__name__ + " on " + func.__name__

        app.logger.debug("running " + log_string)
        try:
            return logic(*args, **kwargs)
        except Exception as e:
            app.logger.error("Failed " + log_string + ", Traceback - " + exception_str(e))
            return render_template("error.html", error=log_string + " failed: " + exception_str(e))
        finally:
            app.logger.debug(log_string + " finished")
    
    def logic(*args, **kwargs):
        # Do stuff here
        return func(*args, **kwargs)

    return wrapper

def argument_decorator(argument):

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log_string = argument_decorator.__name__ + " on " + func.__name__
            
            app.logger.debug("running " + log_string)
            try:
                return logic(argument, *args, **kwargs)
            except Exception as e:
                app.logger.error("Failed " + log_string + ", Traceback - " + exception_str(e))
                return render_template("error.html", error=log_string + " failed: " + exception_str(e))
            finally:
                app.logger.debug(log_string + " finished")
        
        def logic(argument, *args, **kwargs):
            # Do stuff here
            return func(*args, **kwargs)

        return wrapper

    return decorate
"""

def require_auth_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        log_string = require_auth_token.__name__ + " on " + func.__name__

        app.logger.debug("running " + log_string)
        try:
            return logic(*args, **kwargs)
        except Exception as e:
            app.logger.error("Failed " + log_string + ", Traceback - " + exception_str(e))
            return render_template("error.html", error=log_string + " failed: " + exception_str(e))
        finally:
            app.logger.debug(log_string + " finished")
    
    def logic(*args, **kwargs):
        app.logger.info("decoding auth token: " + request.args.get('key'))
        user_id = orm.User.decode_auth_token(request.args.get('key'))
        
        app.logger.info("verifying auth token: " + request.args.get('key'))
        if user_id == "expired" or user_id == "invalid":
            app.logger.info("auth token is " + user_id)
            return abort(401)
        else:
            return func(*args, **kwargs)

    return wrapper

def apply_metrics(endpoint):

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log_string = apply_metrics.__name__ + " on " + func.__name__
            
            app.logger.debug("running " + log_string)
            try:
                return logic(endpoint, *args, **kwargs)
            except Exception as e:
                app.logger.error("Failed " + log_string + ", Traceback - " + exception_str(e))
                return render_template("error.html", error=log_string + " failed: " + exception_str(e))
            finally:
                app.logger.debug(log_string + " finished")
        
        def logic(endpoint, *args, **kwargs):
            view_metric.labels(endpoint=endpoint).inc()
            app.logger.info(endpoint + "loaded")
            
            return func(*args, **kwargs)

        return wrapper

    return decorate


def get_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        log_string = get_user.__name__ + " on " + func.__name__

        app.logger.debug("running " + log_string)
        try:
            return logic(*args, **kwargs)
        except Exception as e:
            app.logger.error("Failed " + log_string + ", Traceback - " + exception_str(e))
            return render_template("error.html", error=log_string + " failed: " + exception_str(e))
        finally:
            app.logger.debug(log_string + " finished")
    
    def logic(*args, **kwargs):
        with Session.begin() as session:
            try:
                # Get user dict
                user_dict = decrypt_user_dict(user_session["user"])
            except KeyError:
                # Cookie not created
                return func(False, *args, **kwargs)

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
                    return func(user, *args, **kwargs)
        return func(False, *args, **kwargs)

    return wrapper
