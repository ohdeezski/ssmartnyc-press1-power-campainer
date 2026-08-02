from datetime import datetime

from app.extensions import db


class Campaign(db.Model):  # type: ignore[name-defined]
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="draft")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # use_alter breaks the campaigns <-> campaign_templates FK cycle so DDL can sort.
    template_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "campaign_templates.id", use_alter=True, name="fk_campaign_template"
        ),
        nullable=True,
    )
    workflow_id = db.Column(db.Integer, db.ForeignKey("workflows.id"), nullable=True)
    settings = db.Column(db.JSON, default={})
    results = db.Column(db.JSON, default={})

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "created_by": self.created_by,
            "settings": self.settings or {},
            "results": self.results or {},
        }


class CampaignTemplate(db.Model):  # type: ignore[name-defined]
    __tablename__ = "campaign_templates"

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(
        db.Integer,
        db.ForeignKey("campaigns.id", use_alter=True, name="fk_template_campaign"),
        nullable=True,
    )
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    settings = db.Column(db.JSON, default={})
    audio_ids = db.Column(db.JSON, default=[])
    template_ids = db.Column(db.JSON, default=[])
    caller_profile_id = db.Column(db.Integer, nullable=True)
    provider_ids = db.Column(db.JSON, default=[])
    workflow_id = db.Column(db.Integer, db.ForeignKey("workflows.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "name": self.name,
            "category": self.category,
            "settings": self.settings or {},
            "audio_ids": self.audio_ids or [],
            "template_ids": self.template_ids or [],
            "caller_profile_id": self.caller_profile_id,
            "provider_ids": self.provider_ids or [],
            "workflow_id": self.workflow_id,
        }


class CampaignRun(db.Model):  # type: ignore[name-defined]
    __tablename__ = "campaign_runs"

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=False)
    run_number = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default="queued")
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)
    total_contacts = db.Column(db.Integer, default=0)
    total_calls = db.Column(db.Integer, default=0)
    total_messages = db.Column(db.Integer, default=0)
    total_emails = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    conversion_count = db.Column(db.Integer, default=0)
    cost = db.Column(db.Float, default=0.0)
    duration = db.Column(db.Integer, default=0)
    settings_snapshot = db.Column(db.JSON, default={})

    def to_dict(self):
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "run_number": self.run_number,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "total_contacts": self.total_contacts,
            "total_calls": self.total_calls,
            "total_messages": self.total_messages,
            "total_emails": self.total_emails,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "conversion_count": self.conversion_count,
            "cost": self.cost,
            "duration": self.duration,
        }
