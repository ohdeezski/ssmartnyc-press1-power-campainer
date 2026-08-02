from app.extensions import db


class ContactList(db.Model):  # type: ignore[name-defined]
    __tablename__ = "contact_lists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    source_file_id = db.Column(db.Integer, db.ForeignKey("stored_files.id"), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="uploaded")
    counts = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    committed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    source_file = db.relationship("StoredFile", backref="contact_lists", lazy=True)
    creator = db.relationship("User", backref="contact_lists", lazy=True)
    contacts = db.relationship("Contact", backref="contact_list", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "source_file_id": self.source_file_id,
            "created_by": self.created_by,
            "status": self.status,
            "counts": self.counts or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "committed_at": self.committed_at.isoformat() if self.committed_at else None,
        }


class Contact(db.Model):  # type: ignore[name-defined]
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    contact_list_id = db.Column(db.Integer, db.ForeignKey("contact_lists.id"), nullable=False)
    phone = db.Column(db.String(20), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    timezone = db.Column(db.String(100), nullable=True)
    consent = db.Column(db.Boolean, nullable=False, default=True)
    consent_source = db.Column(db.String(100), nullable=True)
    tags = db.Column(db.JSON, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="ready")
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    __table_args__ = (
        db.UniqueConstraint("contact_list_id", "phone", name="uq_contact_list_phone"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "contact_list_id": self.contact_list_id,
            "phone": self.phone,
            "name": self.name,
            "email": self.email,
            "timezone": self.timezone,
            "consent": self.consent,
            "consent_source": self.consent_source,
            "tags": self.tags or [],
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
