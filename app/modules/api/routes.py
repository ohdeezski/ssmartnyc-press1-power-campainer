from flask import jsonify
from flask_login import current_user, login_required

from app.extensions import db
from app.modules.api import api_bp
from app.modules.auth.models import User


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Liveness + dependency probe used by load balancers and uptime monitors."""
    from flask import current_app

    from app.socket_events import collect_system_metrics

    status = "healthy"
    services = {
        "database": "connected",
        "storage": "connected",
        "logging": "connected",
        "notifications": "connected",
    }

    # Probe the database with a real round-trip instead of assuming it is up.
    try:
        db.session.execute(db.text("SELECT 1"))
    except Exception:
        status = "unhealthy"
        services["database"] = "unreachable"

    # Probe Redis only when a broker is configured; skip silently otherwise.
    broker = current_app.config.get("CELERY_BROKER_URL", "")
    if broker.startswith("redis://"):
        try:
            import redis

            client = redis.Redis.from_url(broker, socket_connect_timeout=2)
            client.ping()
            services["redis"] = "connected"
        except Exception:
            status = "unhealthy"
            services["redis"] = "unreachable"

    return jsonify(
        {
            "status": status,
            "version": "1.0.0",
            "stage": "foundation",
            "services": services,
            "metrics": collect_system_metrics(),
        }
    )


@api_bp.route("/user", methods=["GET"])
@login_required
def get_user():
    return jsonify(
        {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role,
            "status": current_user.status,
        }
    )


@api_bp.route("/stats", methods=["GET"])
@login_required
def get_stats():
    from app.modules.notifications.models import Notification
    from app.modules.storage.models import StoredFile

    return jsonify(
        {
            "users": User.query.count(),
            "files": StoredFile.query.count(),
            "notifications": Notification.query.filter_by(read=False).count(),
            # .keys() already yields table-name strings; calling .name on them
            # raised AttributeError and made /api/stats a guaranteed 500.
            "database_tables": sorted(db.metadata.tables.keys()),
        }
    )
