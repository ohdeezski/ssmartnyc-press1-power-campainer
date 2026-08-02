# flake8: noqa: F401,E402
from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")

from app.modules.api import routes
