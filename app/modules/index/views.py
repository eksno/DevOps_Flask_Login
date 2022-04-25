from flask import Blueprint, render_template, redirect, url_for
from prometheus_client import generate_latest

from app.components.utils import get_user, apply_metrics

mod = Blueprint("index", __name__, url_prefix="/")


@apply_metrics(endpoint="/")
@mod.route("/")
def index():
    return redirect(url_for("index.home"))

@apply_metrics(endpoint="/home")
@mod.route("/home", methods=["POST", "GET"])
@get_user
def home(user):
    if user is False:
        # User not signed in
        return render_template("home.html")

    return redirect(url_for("user.index"))


@apply_metrics(endpoint="/metrics")
@mod.route("/metrics")
def metrics():
    return generate_latest()
