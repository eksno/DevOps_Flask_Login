from logging import handlers
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from waitress import serve
from datetime import datetime
from flask.logging import default_handler
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import errno


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
    (see environment variables set in docker-compose)
    """
    postgres_user = os.environ["POSTGRES_USER"]
    postgres_pass = os.environ["POSTGRES_PASS"]
    postgres_host = os.environ["POSTGRES_HOST"]
    postgres_port = os.environ["POSTGRES_PORT"]
    postgres_dbname = os.environ["POSTGRES_DBNAME"]
    return f"postgresql://{postgres_user}:{postgres_pass}@{postgres_host}:{postgres_port}/{postgres_dbname}"


def create_handlers(log_fname):
    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = TimedRotatingFileHandler(log_fname)
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.DEBUG)

    # Create formatters and add it to handlers
    c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    f_format = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(name)s - %(levelname)s - %(message)s"
    )
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    return c_handler, f_handler


def configure_logging(app):
    now = datetime.now()

    # Get Loggers
    app_logger = logging.getLogger(__name__)
    flask_logger = logging.getLogger("flask")
    sqlalchemy_logger = logging.getLogger("sqlalchemy")
    waitress_logger = logging.getLogger("waitress")

    # Set root logger level:
    # if (handler level < root level):
    #     root level overrides handler level
    app_logger.setLevel(logging.DEBUG)
    flask_logger.setLevel(logging.DEBUG)
    sqlalchemy_logger.setLevel(logging.DEBUG)
    waitress_logger.setLevel(logging.DEBUG)

    # Create Handlers
    make_sure_path_exists(os.path.join(log_dir, now.strftime("%Y")))
    log_year_dir = os.path.join(log_dir, now.strftime("%Y"))
    make_sure_path_exists(os.path.join(log_year_dir, now.strftime("%B")))
    log_month_dir = os.path.join(log_year_dir, now.strftime("%B"))
    log_fname = os.path.join(
        log_month_dir, "{}.log".format(now.strftime("%b-%d-%Y_%H-%M-%S"))
    )

    c_handler, f_handler = create_handlers(log_fname)

    # Add handlers to the logger
    app_logger.addHandler(c_handler)
    app_logger.addHandler(f_handler)
    app_logger.addHandler(default_handler)

    flask_logger.addHandler(c_handler)
    flask_logger.addHandler(f_handler)

    sqlalchemy_logger.addHandler(c_handler)
    sqlalchemy_logger.addHandler(f_handler)

    waitress_logger.addHandler(c_handler)
    waitress_logger.addHandler(f_handler)

    # app_logger, app.logger, and logging are all the same because they alle are based off __name__
    # In other words, everything have done to app_logger here has synced up automatically with
    # app.logger and logging.
    logging.debug("logging configured")


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = get_connection_url()
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

    configure_logging(app)
    return app


app = create_app()
logging.debug("test debug")

engine = create_engine(get_connection_url())

Session = sessionmaker()
Session.configure(bind=engine)


def serve_app(app):
    serve(app, host="0.0.0.0", port=8080, url_scheme="https")


from app import views


if __name__ == "__name__":
    serve_app()
