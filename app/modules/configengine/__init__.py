# flake8: noqa: F401,E402
from flask import Blueprint

configengine_bp = Blueprint("configengine", __name__, url_prefix="/api/config")

from app.modules.configengine import models, routes, services
