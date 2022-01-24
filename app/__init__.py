"""
def configure_logging():
    logging.dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })"""
import os
import logging
from logging.config import dictConfig
from datetime import datetime
from flask.logging import default_handler
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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


def configure_logging():
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    logging.basicConfig(
        filemode='w',
        filename="app {}".format(datetime.now().strftime("%b-%d-%Y_%H:%M:%S")),

    )

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = get_connection_url()
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

    configure_logging()
    return app

app = create_app()

engine = create_engine(get_connection_url())

Session = sessionmaker()
Session.configure(bind=engine)

from app import views
