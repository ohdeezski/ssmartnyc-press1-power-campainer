# flake8: noqa: F401,E402
from flask import Blueprint

ui_bp = Blueprint("ui", __name__, template_folder="templates")

from app.modules.ui import routes
