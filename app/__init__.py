import os
import errno
import logging

from resources.OpenLogger.open_logger import configure_loggers
from waitress import serve
from datetime import datetime
from flask.logging import default_handler
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from sqlalchemy import create_engine, inspect, sql
from sqlalchemy.orm import sessionmaker


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


root_dir = os.path.normpath(os.getcwd() + os.sep)
make_sure_path_exists(os.path.join(root_dir, "app"))
app_dir = os.path.join(root_dir, "app")
make_sure_path_exists(os.path.join(root_dir, "logs"))
log_dir = os.path.join(app_dir, "logs")


def get_connection_url() -> str:
    """
    Get connection URL from environment variables
    (see environment variables referenced in docker-compose)
    """
    postgres_user = os.environ["POSTGRES_USER"]
    postgres_pass = os.environ["POSTGRES_PASS"]
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

    configure_logging()
    return app


app = create_app()

engine = create_engine(get_connection_url())
insp = inspect(engine)

Session = sessionmaker()
Session.configure(bind=engine)


def serve_app(app):
    serve(app, host="0.0.0.0", port=8080, url_scheme="https")


from app import views


if __name__ == "__name__":
    serve_app()
