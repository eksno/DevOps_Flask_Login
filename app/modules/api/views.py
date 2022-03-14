from flask import Blueprint, request, render_template

from app import app, Session, view_metric
from app.components import orm
from app.components.utils import exception_str
from app.components.cipher import AESCipher


mod = Blueprint("api", __name__, url_prefix="/api")

cipher = AESCipher()