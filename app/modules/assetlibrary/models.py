from datetime import datetime

from app.extensions import db


class Asset(db.Model):  # type: ignore[name-defined]
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    subtype = db.Column(db.String(100))
    file_id = db.Column(db.Integer, db.ForeignKey("stored_files.id"))
    tags = db.Column(db.String(500))
    extra_data = db.Column(db.Text)
    version = db.Column(db.Integer, default=1)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "subtype": self.subtype,
            "file_id": self.file_id,
            "tags": self.tags,
            "extra_data": self.extra_data,
            "version": self.version,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
