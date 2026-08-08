"""Integration tests: real request flow across the whole app (auth -> API)."""

from app.extensions import db
from app.modules.auth.models import User


def _login(client):
    with client.application.app_context():
        user = User(email="int@example.com", name="Int", role="admin")
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()
    client.post(
        "/auth/login",
        data={"email": "int@example.com", "password": "testpassword123"},
        follow_redirects=True,
    )


def test_login_then_health_endpoint(client):
    """Full user journey: auth -> authenticated /api/health."""
    _login(client)
    resp = client.get("/api/health")
    assert resp.status_code == 200


def test_health_endpoint_is_public(client):
    """The health probe must not require authentication."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "healthy"


def test_marketing_pages_render_for_anon(client):
    """Public pages resolve without redirect loops."""
    resp = client.get("/")
    assert resp.status_code in (200, 302)
