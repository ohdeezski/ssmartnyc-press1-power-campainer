from flask import Blueprint

workflow_bp = Blueprint("workflow", __name__, url_prefix="/api/workflows")

from app.modules.workflow import models, routes  # noqa: E402,F401
