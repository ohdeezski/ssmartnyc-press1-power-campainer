"""Configengine write permissions and secret redaction."""

from app.extensions import db as _db
from app.modules.auth.models import User


def _login_as(client, email, password, role):
    with client.application.app_context():
        user = User(email=email, name=role.title(), role=role)
        user.set_password(password)
        _db.session.add(user)
        _db.session.commit()
    client.post("/auth/login", data={"email": email, "password": password})


def test_viewer_cannot_write_system_config(client):
    _login_as(client, "viewer@cfg.com", "password123", "viewer")
    resp = client.post(
        "/api/config/system", json={"key": "max_concurrent", "value": "20"}
    )
    assert resp.status_code == 403


def test_admin_can_write_system_config(auth_user):
    resp = auth_user.post(
        "/api/config/system", json={"key": "max_concurrent", "value": "20"}
    )
    assert resp.status_code == 200


def test_viewer_cannot_set_environment_config(client):
    _login_as(client, "viewer2@cfg.com", "password123", "viewer")
    resp = client.post(
        "/api/config/environment",
        json={
            "environment": "production",
            "app_config": {"X": "1"},
        },
    )
    assert resp.status_code == 403


def test_viewer_cannot_set_feature_flag(client):
    _login_as(client, "viewer3@cfg.com", "password123", "viewer")
    resp = client.post("/api/config/feature-flags", json={"key": "ai", "enabled": True})
    assert resp.status_code == 403


def test_environment_secrets_redacted(auth_user):
    resp = auth_user.post(
        "/api/config/environment",
        json={
            "environment": "production",
            "app_config": {"API_KEY": "super-secret-value", "MAX_WORKERS": "10"},
        },
    )
    assert resp.status_code == 200

    resp = auth_user.get("/api/config/environment?environment=production")
    configs = resp.get_json()["configs"]
    assert configs["app_config"]["API_KEY"] == "***REDACTED***"
    assert configs["app_config"]["MAX_WORKERS"] == "10"
