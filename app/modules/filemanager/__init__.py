# flake8: noqa: F401,E402
from flask import Blueprint

filemanager_bp = Blueprint("filemanager", __name__, url_prefix="/api/files")

from app.modules.filemanager import routes, services
