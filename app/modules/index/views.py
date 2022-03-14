from flask import Blueprint, render_template, redirect, url_for
from prometheus_client import generate_latest

from app import app, view_metric
from app.components.utils import get_signed_in

mod = Blueprint("index", __name__, url_prefix="/")


@mod.route("/")
def index():
    view_metric.labels(endpoint="/").inc()
    app.logger.info("/ loaded")

    return redirect(url_for("index.home"))

@mod.route("/home", methods=["POST", "GET"])
@get_signed_in
def home(user):
    view_metric.labels(endpoint="/home").inc()
    app.logger.info("/home loaded")

    if user is False:
        # User not signed in
        return render_template("home.html")

    return redirect(url_for("user.index"))


@mod.route("/metrics")
def metrics():
    view_metric.labels(endpoint="/metrics").inc()
    return generate_latest()
