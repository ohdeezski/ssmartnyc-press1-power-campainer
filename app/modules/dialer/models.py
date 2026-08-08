from app.extensions import db

# Provider model moved to app.modules.providers.models
# Keep a re-export here for backward compatibility
from app.modules.providers.models import (  # noqa: F401
    CallerProfile,
    Connection,
    NumberPool,
    Provider,
)


class Call(db.Model):  # type: ignore[name-defined]
    __tablename__ = "calls"

    id = db.Column(db.Integer, primary_key=True)
    campaign_run_id = db.Column(
        db.Integer, db.ForeignKey("campaign_runs.id"), nullable=False
    )
    contact_phone = db.Column(db.String(20), nullable=False)
    status = db.Column(
        db.String(20), nullable=False, default="not_started"
    )  # not_started|preparing|dialing|ringing|answered|press1|transferring|complete|failed|blocked|voicemail|no_answer|retrying  # noqa: E501
    outcome = db.Column(db.String(50), nullable=True)
    press1_detected = db.Column(db.Boolean, nullable=False, default=False)
    digits = db.Column(db.String(20), nullable=True)
    duration_sec = db.Column(db.Integer, nullable=True)
    attempt = db.Column(db.Integer, nullable=False, default=1)
    status_history = db.Column(db.JSON, nullable=True)
    call_uuid = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    finished_at = db.Column(db.DateTime(timezone=True), nullable=True)

    campaign_run = db.relationship(
        "CampaignRun", backref=db.backref("calls", lazy="dynamic")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "campaign_run_id": self.campaign_run_id,
            "contact_phone": self.contact_phone,
            "status": self.status,
            "outcome": self.outcome,
            "press1_detected": self.press1_detected,
            "digits": self.digits,
            "duration_sec": self.duration_sec,
            "attempt": self.attempt,
            "status_history": self.status_history or [],
            "call_uuid": self.call_uuid,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }


class Message(db.Model):  # type: ignore[name-defined]
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    campaign_run_id = db.Column(
        db.Integer, db.ForeignKey("campaign_runs.id"), nullable=False
    )
    contact_phone = db.Column(db.String(20), nullable=False)
    channel = db.Column(db.String(20), nullable=False)  # sms|email|whatsapp
    status = db.Column(db.String(20), nullable=False, default="queued")
    provider_message_id = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    sent_at = db.Column(db.DateTime(timezone=True), nullable=True)

    campaign_run = db.relationship(
        "CampaignRun", backref=db.backref("messages", lazy="dynamic")
    )


class Conversation(db.Model):  # type: ignore[name-defined]
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    campaign_run_id = db.Column(
        db.Integer, db.ForeignKey("campaign_runs.id"), nullable=False
    )
    contact_phone = db.Column(db.String(20), nullable=False)
    channel = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="started")
    events = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    campaign_run = db.relationship(
        "CampaignRun", backref=db.backref("conversations", lazy="dynamic")
    )
