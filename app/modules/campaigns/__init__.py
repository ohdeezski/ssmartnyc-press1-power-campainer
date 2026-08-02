# flake8: noqa: F401,E402
from flask import Blueprint

campaigns_bp = Blueprint(
    "campaigns", __name__, url_prefix="/campaigns", template_folder="templates"
)

from app.modules.campaigns import models, routes, services
