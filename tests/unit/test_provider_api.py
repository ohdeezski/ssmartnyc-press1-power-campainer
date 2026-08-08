"""Provider API wiring smoke: the blueprint must actually mount.

Regression guard for a bug where ``routes.py`` redefined ``providers_bp``
instead of importing it from the package, so every /api/providers route
ran on an orphan blueprint and returned 404.
"""

from app.extensions import db
from app.modules.auth.models import User


def _login(client):
    client.post(
        "/auth/login",
        data={"email": "prov@example.com", "password": "testpassword123"},
        follow_redirects=True,
    )


def test_provider_api_route_registered(app):
    rules = {str(r) for r in app.url_map.iter_rules()}
    assert "/api/providers/" in rules
    assert "/api/providers/<int:provider_id>/test" in rules
    assert "/api/providers/failover" in rules


def test_provider_crud_roundtrip(client):
    with client.application.app_context():
        user = User(email="prov@example.com", name="P", role="admin")
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()
    _login(client)

    resp = client.post(
        "/api/providers/",
        json={
            "kind": "asterisk",
            "channel": "voice",
            "config": {"host": "127.0.0.1", "port": 5038},
        },
    )
    assert resp.status_code == 201
    provider_id = resp.get_json()["id"]

    listing = client.get("/api/providers/")
    assert listing.status_code == 200
    assert any(p["id"] == provider_id for p in listing.get_json())


def test_provider_rejects_unknown_kind(client):
    with client.application.app_context():
        user = User(email="prov@example.com", name="P", role="admin")
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()
    _login(client)
    resp = client.post(
        "/api/providers/",
        json={"kind": "smoke-signal", "config": {}},
    )
    assert resp.status_code == 400


def test_messaging_provider_kinds_accepted(client):
    with client.application.app_context():
        user = User(email="prov@example.com", name="P", role="admin")
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()
    _login(client)
    for kind in ("whatsapp", "smtp", "telegram"):
        resp = client.post(
            "/api/providers/",
            json={"kind": kind, "config": {"token": "abc", "user": "u"}},
        )
        assert resp.status_code == 201, f"{kind} -> {resp.status_code}"
        assert resp.get_json()["kind"] == kind
