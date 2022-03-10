from flask import Blueprint, render_template, request, jsonify
from prometheus_client import generate_latest, Counter, Summary

import logging
import sqlalchemy as sa

from app import app, Session, engine, insp


view_metric = Counter("view", "Endpoint View", ["endpoint"])
load_duration_metric = Summary("load_duration", "Time spent loading sql pages")


@app.route("/")
@app.route("/home", methods=["POST", "GET"])
def home():
    view_metric.labels(endpoint="/home").inc()
    logging.info("/ or /home loaded")

    # TODO: check if user is signed in

    return render_template("not_signed_in.html")


@app.route("/metrics")
def metrics():
    view_metric.labels(endpoint="/metrics").inc()
    return generate_latest()
