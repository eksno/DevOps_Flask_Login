from flask import render_template, request, jsonify
from prometheus_client import generate_latest, Counter, Summary

import logging
import sqlalchemy as sa

from app import app, Session, insp

import app.orm.database as orm

view_metric = Counter("view", "Endpoint View", ["endpoint"])
load_duration_metric = Summary("load_duration", "Time spent loading sql pages")


@app.route("/")
@app.route("/home", methods=["POST", "GET"])
def home():
    view_metric.labels(endpoint="/home").inc()
    logging.info("/ or /home loaded")

    # TODO: check if user is signed in

    return render_template("not_signed_in.html")


@app.route("/signin", methods=["POST", "GET"])
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
            exists = (
                session.query(orm.User)
                .filter(orm.User.email == userdata["E-Mail"])
                .scalar()
            )
        app.logger.debug("session closed")

        if not exists:
            app.logger.debug(userdata["E-Mail"] + " does not exist.")
            # User does not exist
            return render_template(
                "signin.html", message="User does not exist."
            )  # TODO: Give a better message telling the person the user already exists

        # User exists
        app.logger.debug(userdata["E-Mail"] + " does exist, logging in...")

        # TODO: check password and properly login

        return render_template("redirect.html", url="/home")

    app.logger.debug("default operation")
    # Default operation
    return render_template("signin.html", message="Haven't signed up yet?")


@app.route("/signup", methods=["POST", "GET"])
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

        encrypted_password = "testing123"
        user_token = "123testing"

        new_user = orm.User(email=userdata["E-Mail"], username=userdata["Username"])
        new_password = orm.Password(password=encrypted_password, user=new_user)
        new_user_token = orm.UserToken(user_token=user_token, user=new_user)

        app.logger.debug("creating and beginning database session...")
        with Session.begin() as session:
            app.logger.debug("session created and started")

            if (
                session.query(orm.User)
                .filter(orm.User.email == userdata["E-Mail"])
                .scalar()
            ):
                app.logger.debug(userdata["E-Mail"] + " already exists...")
                return "signup.html"  # TODO: Give some message telling the person the user already exists

            session.add(new_user)
            session.add(new_password)
            session.add(new_user_token)
        app.logger.debug("session closed")

        # TODO: actually sign in.

        return render_template("redirect.html", url="/home")

    # Default operation
    return render_template("signup.html")


@app.route("/metrics")
def metrics():
    view_metric.labels(endpoint="/metrics").inc()
    return generate_latest()
