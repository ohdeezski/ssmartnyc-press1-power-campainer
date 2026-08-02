# flake8: noqa: F401,E402
from flask import Blueprint

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
    template_folder="templates",
    static_folder="static",
)

from app.modules.auth import forms, models, routes
