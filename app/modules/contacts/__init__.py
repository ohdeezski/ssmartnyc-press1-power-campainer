# flake8: noqa: F401,E402
from flask import Blueprint

contacts_bp = Blueprint("contacts", __name__, url_prefix="/api/contacts")

from app.modules.contacts import models, routes, services
