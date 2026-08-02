from flask import jsonify, request
from flask_login import current_user, login_required

from app.modules.events import events_bp
from app.modules.events.models import Event, AuditLog
from app.modules.events.services import publish_event


@events_bp.route("/live", methods=["GET"])
@login_required
def live_events():
    run_id = request.args.get("run_id", type=int)
    limit = request.args.get("limit", 50, type=int)

    query = Event.query.order_by(Event.created_at.desc())
    if run_id:
        query = query.filter(Event.entity_id == run_id)
    events = query.limit(limit).all()
    return jsonify([e.to_dict() for e in reversed(events)])


@events_bp.route("/publish", methods=["POST"])
@login_required
def publish_event_endpoint():
    data = request.get_json()
    if not data or not data.get("action"):
        return jsonify({"error": "action is required"}), 400

    event = publish_event(
        entity_type=data.get("entity_type", "campaign"),
        entity_id=data.get("entity_id"),
        action=data["action"],
        message_human=data.get("message_human"),
        level=data.get("level", "info"),
        payload=data.get("payload", {}),
        user_id=current_user.id,
    )
    return jsonify(event.to_dict()), 201


@events_bp.route("/audit", methods=["GET"])
@login_required
def list_audit_logs():
    limit = request.args.get("limit", 100, type=int)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return jsonify([log.to_dict() for log in logs])
