import os

from flask import Flask, jsonify, render_template, request

from app.extensions import csrf, db, login_manager, migrate, socketio


@login_manager.user_loader
def load_user(user_id):
    from app.modules.auth.models import User

    return db.session.get(User, int(user_id))


def _register_blueprints(app):
    from app.modules.api import api_bp
    from app.modules.assetlibrary import assetlibrary_bp
    from app.modules.auth import auth_bp
    from app.modules.campaigns import campaigns_bp
    from app.modules.configengine import configengine_bp
    from app.modules.contacts import contacts_bp
    from app.modules.dialer import dialer_bp
    from app.modules.events import events_bp
    from app.modules.filemanager import filemanager_bp
    from app.modules.notifications import notifications_bp
    from app.modules.providers import providers_bp
    from app.modules.taskqueue import taskqueue_bp
    from app.modules.ui import ui_bp
    from app.modules.workflow import workflow_bp

    for blueprint in (
        auth_bp,
        ui_bp,
        api_bp,
        campaigns_bp,
        filemanager_bp,
        assetlibrary_bp,
        configengine_bp,
        notifications_bp,
        taskqueue_bp,
        workflow_bp,
        contacts_bp,
        dialer_bp,
        events_bp,
        providers_bp,
    ):
        app.register_blueprint(blueprint)


def _register_error_handlers(app):
    def _wants_json():
        return (
            request.path.startswith("/api/")
            or request.accept_mimetypes.best == "application/json"
        )

    @app.errorhandler(404)
    def not_found(error):
        if _wants_json():
            return jsonify({"error": "Not found"}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(error):
        if _wants_json():
            return jsonify({"error": "Forbidden"}), 403
        return render_template("errors/403.html"), 403

    @app.errorhandler(413)
    def too_large(error):
        return jsonify({"error": "Uploaded file exceeds the maximum allowed size"}), 413

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        app.logger.exception("Unhandled server error")
        if _wants_json():
            return jsonify({"error": "Internal server error"}), 500
        return render_template("errors/500.html"), 500


def _register_context_processors(app):
    @app.context_processor
    def inject_unread_count():
        from flask_login import current_user

        from app.modules.notifications.models import Notification

        if current_user.is_authenticated:
            count = Notification.query.filter_by(
                user_id=current_user.id, read=False
            ).count()
        else:
            count = 0
        return {"unread_count": count}


def _register_template_filters(app):
    @app.template_filter("human_size")
    def human_size(num_bytes):
        """Render a byte count as a readable size (e.g. 12.4 MB)."""
        if not num_bytes:
            return "0 B"
        size = float(num_bytes)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size < 1024 or unit == "TB":
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


def create_app(config_class=None):
    app = Flask(__name__)

    if config_class is None:
        config_class = os.environ.get("FLASK_ENV", "development")

    from app.config import config

    config_object = config.get(config_class, config["development"])
    app.config.from_object(config_object)

    # Ensure writable runtime directories exist before anything touches them.
    for path in (app.config.get("UPLOAD_FOLDER"), app.instance_path):
        if path:
            os.makedirs(path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins=app.config.get("CORS_ORIGINS", "*"))
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"
    csrf.init_app(app)

    # Socket handlers for the live dashboard telemetry (registers @socketio.on).
    from app import socket_events  # noqa: F401

    _register_context_processors(app)
    _register_template_filters(app)

    # Point the shared Celery instance at this app's broker/backend config so
    # the web process and the worker agree. Tasks stay eagerly-executed in
    # testing (CELERY_TASK_ALWAYS_EAGER=True) and need no live broker.
    from app.extensions.celery import celery

    celery.conf.update(
        broker_url=app.config.get("CELERY_BROKER_URL"),
        result_backend=app.config.get("CELERY_RESULT_BACKEND"),
        task_always_eager=app.config.get("CELERY_TASK_ALWAYS_EAGER", False),
    )

    from app.modules.logging_module import setup_logging

    setup_logging(app)

    _register_blueprints(app)
    _register_error_handlers(app)

    # Import every model so create_all()/migrations see the full metadata.
    with app.app_context():
        from app.modules.assetlibrary import models as _asset_models  # noqa: F401
        from app.modules.auth import models as _auth_models  # noqa: F401
        from app.modules.campaigns import models as _campaign_models  # noqa: F401
        from app.modules.configengine import models as _config_models  # noqa: F401
        from app.modules.contacts import models as _contacts_models  # noqa: F401
        from app.modules.dialer import models as _dialer_models  # noqa: F401
        from app.modules.events import models as _events_models  # noqa: F401
        from app.modules.notifications import models as _notif_models  # noqa: F401
        from app.modules.providers import models as _providers_models  # noqa: F401
        from app.modules.storage import models as _storage_models  # noqa: F401
        from app.modules.workflow import models as _workflow_models  # noqa: F401

        if app.config.get("AUTO_CREATE_TABLES", True):
            db.create_all()

    if hasattr(config_object, "init_app"):
        config_object.init_app(app)

    return app
