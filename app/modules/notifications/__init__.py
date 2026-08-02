# flake8: noqa: F401,E402
from flask import Blueprint

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

from app.modules.notifications import models, routes, services
