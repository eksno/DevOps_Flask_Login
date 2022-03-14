# /app/__init__.py

import os
import logging

from flask import Flask
from waitress import serve
from prometheus_client import make_wsgi_app, Counter, Summary
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, inspect

from app.components.OpenLogger import configure_loggers


def get_connection_url() -> str:
    """
    Get connection URL from environment variables
    (see environment variables referenced in docker-compose)
    """
    postgres_user = os.environ["POSTGRES_USER"]
    postgres_pass = os.environ["POSTGRES_PASSWORD"]
    postgres_host = os.environ["POSTGRES_HOST"]
    postgres_port = os.environ["POSTGRES_PORT"]
    postgres_dbname = os.environ["POSTGRES_DBNAME"]
    return f"postgresql://{postgres_user}:{postgres_pass}@{postgres_host}:{postgres_port}/{postgres_dbname}"


def configure_logging():
    app_logger = logging.getLogger(__name__)
    flask_logger = logging.getLogger("flask")
    sqlalchemy_logger = logging.getLogger("sqlalchemy")
    waitress_logger = logging.getLogger("waitress")

    configure_loggers(
        [app_logger, flask_logger, sqlalchemy_logger, waitress_logger], log_to_file=True
    )


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = get_connection_url()
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})
    app.secret_key = os.environ["SECRET_KEY"]

    configure_logging()
    return app


def create_session(engine):
    Session = sessionmaker()
    Session.configure(bind=engine)
    return Session


app = create_app()
engine = create_engine(get_connection_url())
insp = inspect(engine)
Session = create_session(engine)

view_metric = Counter("view", "Endpoint View", ["endpoint"])
load_duration_metric = Summary("load_duration", "Time spent loading sql pages")


""" Modules """

# Index Module
from app.modules.index import index_mod

app.register_blueprint(index_mod)

# Auth Module
from app.modules.auth import auth_mod

app.register_blueprint(auth_mod)

# User Module
from app.modules.user import user_mod

app.register_blueprint(user_mod)

# API Module
from app.modules.api import api_mod

app.register_blueprint(api_mod)


def serve_app(app):
    serve(app, host="0.0.0.0", port=os.environ["FLASK_PORT"], url_scheme="https")


if __name__ == "__name__":
    serve_app()
