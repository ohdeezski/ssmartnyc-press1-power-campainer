# flake8: noqa: F401,E402
from flask import Blueprint

dialer_bp = Blueprint("dialer", __name__, url_prefix="/api/dialer")

from app.modules.dialer import models, backends, tasks, services, routes
