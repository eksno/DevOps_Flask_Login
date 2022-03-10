from flask import Blueprint, render_template
from prometheus_client import generate_latest

from app import app, view_metric

mod = Blueprint("index", __name__, url_prefix="/")


@mod.route("/")
@mod.route("/home", methods=["POST", "GET"])
def home():
    view_metric.labels(endpoint="/home").inc()
    app.logger.info("/ or /home loaded")

    # TODO: check if user is signed in

    return render_template("not_signed_in.html")


@mod.route("/metrics")
def metrics():
    view_metric.labels(endpoint="/metrics").inc()
    return generate_latest()
