from flask import render_template, request, jsonify
from prometheus_client import generate_latest, Counter, Summary

import logging
import psycopg2

from app import app, Session, get_connection_url, logger

import orm.database as orm

view_metric = Counter("view", "Endpoint View", ["endpoint"])
load_duration_metric = Summary("load_duration", "Time spent loading sql pages")


@app.route("/")
@app.route("/home", methods=["POST", "GET"])
def home():
    view_metric.labels(endpoint="/home").inc()
    app.logger.info("/ or /home loaded")

    # TODO: check if user is signed in

    return render_template("not_signed_in.html")


@app.route("/signin", methods=["POST", "GET"])
def signin():
    logger.info("/signin loaded")

    if request.method == "POST":
        logger.debug("post request")
        userdata = request.form

        if len(userdata) == 2:

            conn = psycopg2.connect(get_connection_url())
            logger.debug("connected to database")

            # Check if user exists
            with conn.cursor() as cur:
                logger.debug("opened cursor")
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

            logger.debug("exited cursor")

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
    return render_template("signin.html", message="Haven't signed up yet?")


@app.route("/signup")
def signup():

    if request.method == "POST":
        userdata = request.form

        logger.info(userdata)

        # TODO: Add more bad data checks
        if len(userdata) != 3:
            return render_template("error.html", message="Bad Data")

        # TODO: check if userdata is valid

        # Add user

        encrypted_password = "testing123"
        user_token = "123testing"

        new_user = orm.User(email=userdata["E-Mail"], username=userdata["Username"])
        new_password = orm.Password(password=encrypted_password, user=new_user)
        new_user_token = orm.UserToken(user_token=user_token, user=new_user)

        logger.debug("creating and beginning database session...")
        with Session.begin() as session:
            logger.debug("session created and started")
            session.add(new_user)
            session.add(new_password)
            session.add(new_user_token)
        logger.debug("session closed")

        # TODO: actually sign in.

        return render_template("redirect.html", url="/home")

    # Default operation
    return render_template("signup.html")


@app.route("/metrics")
def metrics():
    return generate_latest()
