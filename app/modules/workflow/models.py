from datetime import datetime

from app.extensions import db


class Workflow(db.Model):  # type: ignore[name-defined]
    """Automation pipeline definition. Spec: docs/version-1.0-spec.md L110."""

    __tablename__ = "workflows"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    campaign_type = db.Column(db.String(50))
    description = db.Column(db.String(500))
    steps = db.Column(db.JSON, default=list)
    status = db.Column(db.String(20), default="draft")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "campaign_type": self.campaign_type,
            "description": self.description,
            "steps": self.steps or [],
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Rule(db.Model):  # type: ignore[name-defined]
    """Conditional branch inside a workflow. Spec L111."""

    __tablename__ = "rules"

    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey("workflows.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    condition = db.Column(db.JSON, default=dict)
    action = db.Column(db.JSON, default=dict)
    delay_seconds = db.Column(db.Integer, default=0)
    max_retries = db.Column(db.Integer, default=0)
    priority = db.Column(db.Integer, default=100)

    def to_dict(self):
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "name": self.name,
            "condition": self.condition or {},
            "action": self.action or {},
            "delay_seconds": self.delay_seconds,
            "max_retries": self.max_retries,
            "priority": self.priority,
        }


class Event(db.Model):  # type: ignore[name-defined]
    """Event-bus record. Spec L114."""

    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False, index=True)
    entity_type = db.Column(db.String(100))
    entity_id = db.Column(db.Integer)
    data = db.Column(db.JSON, default=dict)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    processed = db.Column(db.Boolean, default=False, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "data": self.data or {},
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "processed": self.processed,
        }
