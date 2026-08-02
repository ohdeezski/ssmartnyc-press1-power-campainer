# flake8: noqa: F401,E402
from flask import Blueprint

events_bp = Blueprint("events", __name__, url_prefix="/api/events")

from app.modules.events import models, routes, services
