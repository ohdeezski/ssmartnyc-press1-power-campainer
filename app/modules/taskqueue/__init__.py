# flake8: noqa: F401,E402
from flask import Blueprint

taskqueue_bp = Blueprint("taskqueue", __name__, url_prefix="/api/tasks")

from app.modules.taskqueue import routes
