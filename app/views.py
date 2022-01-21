from flask import render_template, request, jsonify
from prometheus_client import generate_latest, Counter, Summary

import os
import logging
import psycopg2

from app import app, Session

import orm.database as orm

view_metric = Counter("view", "Endpoint View", ["endpoint"])
load_duration_metric = Summary("load_duration", "Time spent loading sql pages")


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


@app.route("/")
@app.route("/home", methods = ['POST', 'GET'])
def home():
    view_metric.labels(endpoint="/home").inc()
    logging.info("/ or /home loaded")

    # TODO: check if user is signed in
    
    return render_template("not_signed_in.html")

@app.route("/signin", methods = ['POST', 'GET'])
def signin():

    if request.method == 'POST':
        userdata = request.form

        if len(userdata) == 2:
            
            conn = psycopg2.connect(
                os.environ.get("DATABASE_URL", "postgres://postgres:postgres@db:5432/postgres")
            )
            logging.debug("connected to database")
            
            # Check if user exists
            with conn.cursor() as cur:
                logging.debug("opened cursor")
                cur.execute(
                    """
                    SELECT
                        email
                    FROM
                        users
                    WHERE
                        email = %(email)s
                    """,
                    {"email": userdata["E-Mail"]},
                )
                exists = cur.fetchone() is not None

            logging.debug("exited cursor")

            if not exists:
                # User does not exist
                return render_template("signin.html", message="User does not exist.")
            else:
                # User exists

                # TODO: check password and properly login

                return render_template("redirect.html", url="/home")
        else:
            # Data is bad, return error
            return render_template("error.html", message="Bad Data")
    
    # Default operation
    return render_template("signin.html")

@app.route("/signup")
def signup():

    if request.method == 'POST':
        userdata = request.form

        #TODO: Add more bad data checks
        if len(userdata) != 3:
            return render_template("error.html", message="Bad Data")

        #TODO: check if userdata is valid

        # Add user
        logging.debug("creating database session")
        with Session() as session:
            logging.debug("session created")
            
            encrypted_password = "testing123"
            user_token = "123testing"

            new_user = orm.User(email=userdata["E-Mail"], username=userdata["Username"])
            new_password = orm.Password(password=encrypted_password)
            new_user_token = orm.UserToken(user_token=user_token)

        # TODO: actually sign in.

        return render_template("redirect.html", url="/home")

    
    # Default operation
    return render_template("signup.html")

@app.route("/metrics")
def metrics():
    return generate_latest()
