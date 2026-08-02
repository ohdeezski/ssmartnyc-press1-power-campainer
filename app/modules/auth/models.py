from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):  # type: ignore[name-defined]
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="viewer")
    status = db.Column(db.String(50), nullable=False, default="active")
    mfa_enabled = db.Column(db.Boolean, default=False)
    mfa_secret = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(45))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        # Must be a property: Flask-Login reads it as an attribute, so the old
        # method form was always truthy and let suspended users log in.
        return self.status == "active"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def has_permission(self, permission):
        role_permissions = {
            "admin": [
                "create_campaign",
                "edit_campaign",
                "delete_campaign",
                "launch_campaign",
                "stop_campaign",
                "view_all",
                "edit_settings",
                "manage_users",
                "view_audit_log",
                "manage_providers",
                "manage_assets",
                "export_data",
            ],
            "manager": [
                "create_campaign",
                "edit_campaign",
                "launch_campaign",
                "stop_campaign",
                "view_all",
                "export_data",
            ],
            "operator": [
                "create_campaign",
                "edit_campaign",
                "launch_campaign",
                "stop_campaign",
                "view_own",
            ],
            "viewer": ["view_own"],
        }
        return permission in role_permissions.get(self.role, [])
