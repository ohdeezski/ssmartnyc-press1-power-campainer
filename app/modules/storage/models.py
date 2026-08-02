from app.extensions import db


class StoredFile(db.Model):  # type: ignore[name-defined]
    __tablename__ = "stored_files"

    id = db.Column(db.Integer, primary_key=True)
    original_name = db.Column(db.String(500), nullable=False)
    stored_name = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    subcategory = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(1000), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    file_extension = db.Column(db.String(20))
    version = db.Column(db.Integer, default=1)
    tags = db.Column(db.String(500))
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "original_name": self.original_name,
            "stored_name": self.stored_name,
            "category": self.category,
            "subcategory": self.subcategory,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_extension": self.file_extension,
            "version": self.version,
            "tags": self.tags,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
