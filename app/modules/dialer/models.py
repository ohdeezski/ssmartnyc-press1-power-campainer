from app.extensions import db


class Provider(db.Model):  # type: ignore[name-defined]
    __tablename__ = "providers"

    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(
        db.String(50), nullable=False
    )  # asterisk, twilio, telnyx, smtp, telegram, whatsapp
    channel = db.Column(db.String(20), nullable=False)  # voice, messaging, email
    status = db.Column(db.String(20), nullable=False, default="disconnected")
    priority = db.Column(db.Integer, nullable=False, default=1)
    latency_ms = db.Column(db.Integer, nullable=True)
    last_health_check_at = db.Column(db.DateTime(timezone=True), nullable=True)
    config = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "kind": self.kind,
            "channel": self.channel,
            "status": self.status,
            "priority": self.priority,
            "latency_ms": self.latency_ms,
            "last_health_check_at": (
                self.last_health_check_at.isoformat()
                if self.last_health_check_at
                else None
            ),
            "config": self.config or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Connection(db.Model):  # type: ignore[name-defined]
    __tablename__ = "provider_connections"

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.id"), nullable=False)
    credentials = db.Column(
        db.Text, nullable=True
    )  # plaintext; Fernet encryption in Phase 5
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    provider = db.relationship("Provider", backref=db.backref("connections", lazy=True))


class CallerProfile(db.Model):  # type: ignore[name-defined]
    __tablename__ = "caller_profiles"

    id = db.Column(db.Integer, primary_key=True)
    caller_name = db.Column(db.String(200), nullable=False)
    number = db.Column(db.String(20), nullable=True)
    sip_trunk = db.Column(db.String(200), nullable=True)
    outbound_route = db.Column(db.String(200), nullable=True)
    caller_id_prefix = db.Column(db.String(20), nullable=True)
    stir_shaken = db.Column(db.Boolean, nullable=False, default=False)
    rotation_mode = db.Column(
        db.String(20), nullable=False, default="fixed"
    )  # fixed|sequential|round_robin|random|weighted|smart
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "caller_name": self.caller_name,
            "number": self.number,
            "sip_trunk": self.sip_trunk,
            "outbound_route": self.outbound_route,
            "caller_id_prefix": self.caller_id_prefix,
            "stir_shaken": self.stir_shaken,
            "rotation_mode": self.rotation_mode,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class NumberPool(db.Model):  # type: ignore[name-defined]
    __tablename__ = "number_pools"

    id = db.Column(db.Integer, primary_key=True)
    caller_profile_id = db.Column(
        db.Integer, db.ForeignKey("caller_profiles.id"), nullable=False
    )
    number = db.Column(db.String(20), nullable=False)
    weight = db.Column(db.Integer, nullable=False, default=1)
    used_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    profile = db.relationship(
        "CallerProfile", backref=db.backref("number_pool", lazy=True)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "caller_profile_id": self.caller_profile_id,
            "number": self.number,
            "weight": self.weight,
            "used_count": self.used_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Call(db.Model):  # type: ignore[name-defined]
    __tablename__ = "calls"

    id = db.Column(db.Integer, primary_key=True)
    campaign_run_id = db.Column(
        db.Integer, db.ForeignKey("campaign_runs.id"), nullable=False
    )
    contact_phone = db.Column(db.String(20), nullable=False)
    status = db.Column(
        db.String(20), nullable=False, default="not_started"
    )  # not_started|preparing|dialing|ringing|answered|press1|transferring|complete|failed|blocked|voicemail|no_answer|retrying
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
