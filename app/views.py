from app import app
from flask import render_template, jsonify
from prometheus_client import generate_latest, Counter, Summary

import os
import logging
import psycopg2


view_metric = Counter("view", "Endpoint View", ["endpoint"])
load_duration_metric = Summary("load_duration", "Time spent loading sql pages")


@app.route("/")
@app.route("/home")
def home():
    view_metric.labels(endpoint="/home").inc()
    logging.info("/ or /home loaded")
    return render_template("home.html")


@app.route("/metrics")
def metrics():
    return generate_latest()
