# flake8: noqa: F401,E402
from app.extensions.celery import celery
from app.extensions.csrf import csrf
from app.extensions.db import db
from app.extensions.login_manager import login_manager
from app.extensions.migrate import migrate
from app.extensions.socketio import socketio
