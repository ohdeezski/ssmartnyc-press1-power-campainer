# flake8: noqa: F401,E402
from flask import Blueprint

assetlibrary_bp = Blueprint("assetlibrary", __name__, url_prefix="/api/assets")

from app.modules.assetlibrary import models, routes, services
