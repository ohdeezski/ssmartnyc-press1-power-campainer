from app.extensions import db, socketio
from app.modules.events.models import Event, AuditLog


def publish_event(entity_type, entity_id, action, message_human=None, level="info", payload=None, user_id=None):
    """Publish an event: write to DB and emit via SocketIO."""
    event = Event(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        message_human=message_human,
        level=level,
        payload=payload or {},
    )
    db.session.add(event)
    db.session.commit()

    # Emit via SocketIO to the campaign room if entity_id is a run_id
    if entity_type == "campaign" and entity_id:
        socketio.emit(
            "campaign_event",
            {
                "run_id": entity_id,
                "action": action,
                "message": message_human,
                "level": level,
                "payload": payload or {},
            },
            room=f"campaign:{entity_id}",
        )

    return event


def log_audit(user_id, action, entity_type=None, entity_id=None, details=None, ip_address=None):
    """Write an audit log entry."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
        ip_address=ip_address,
    )
    db.session.add(entry)
    db.session.commit()
    return entry
