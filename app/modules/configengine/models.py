from datetime import datetime

from app.extensions import db


class SystemConfig(db.Model):  # type: ignore[name-defined]
    """System-wide configuration settings"""

    __tablename__ = "system_configs"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(500))
    category = db.Column(db.String(50), default="general")
    is_secret = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "description": self.description,
            "category": self.category,
            "is_secret": self.is_secret,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class EnvironmentConfig(db.Model):  # type: ignore[name-defined]
    """Environment-specific configuration"""

    __tablename__ = "environment_configs"

    id = db.Column(db.Integer, primary_key=True)
    environment = db.Column(
        db.String(20), nullable=False
    )  # development, testing, production
    app_config = db.Column(db.JSON, default={})
    feature_flags = db.Column(db.JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "environment": self.environment,
            "app_config": self.app_config or {},
            "feature_flags": self.feature_flags or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
