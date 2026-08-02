"""CSRF regression tests: campaign forms must POST successfully in dev config.

The dev/prod configs enable WTF_CSRF_ENABLED, but the routes never passed a form
and the templates never rendered a csrf token, so every campaign POST 400'd.
These tests prove the forms carry a token and reject requests without one.
"""

import re

from app.modules.campaigns.models import Campaign


def _login(client, email="csrfa@test.com"):
    from app.extensions import db as _db
    from app.modules.auth.models import User

    with client.application.app_context():
        user = User(email=email, name="CSRF User", role="admin")
        user.set_password("password123")
        _db.session.add(user)
        _db.session.commit()
    client.post("/auth/login", data={"email": email, "password": "password123"})


def _extract_csrf(resp):
    match = re.search(rb'name="csrf_token"[^>]*value="([^"]+)"', resp.data)
    assert match, "csrf_token hidden input not rendered in form"
    return match.group(1).decode()


def test_campaign_new_requires_and_accepts_csrf(app, client):
    _login(client)
    app.config["WTF_CSRF_ENABLED"] = True
    token = _extract_csrf(client.get("/campaigns/new"))
    # Without a token the POST is rejected.
    resp = client.post("/campaigns/new", data={"name": "No Token", "type": "voice"})
    assert resp.status_code == 400
    # With the rendered token it succeeds.
    resp = client.post(
        "/campaigns/new",
        data={
            "name": "With Token",
            "type": "voice",
            "csrf_token": token,
        },
    )
    assert resp.status_code == 302


def test_campaign_launch_pause_stop_with_csrf(app, client):
    _login(client)
    app.config["WTF_CSRF_ENABLED"] = True
    token = _extract_csrf(client.get("/campaigns/new"))
    resp = client.post(
        "/campaigns/new",
        data={
            "name": "Lifecycle",
            "type": "voice",
            "csrf_token": token,
        },
    )
    assert resp.status_code == 302
    with client.application.app_context():
        campaign_id = Campaign.query.filter_by(name="Lifecycle").first().id

    token = _extract_csrf(client.get(f"/campaigns/{campaign_id}"))
    resp = client.post(f"/campaigns/{campaign_id}/launch", data={"csrf_token": token})
    assert resp.status_code == 302
    token = _extract_csrf(client.get(f"/campaigns/{campaign_id}"))
    resp = client.post(f"/campaigns/{campaign_id}/pause", data={"csrf_token": token})
    assert resp.status_code == 302
    token = _extract_csrf(client.get(f"/campaigns/{campaign_id}"))
    resp = client.post(f"/campaigns/{campaign_id}/stop", data={"csrf_token": token})
    assert resp.status_code == 302
    with client.application.app_context():
        assert Campaign.query.get(campaign_id).status == "finished"


def test_campaign_edit_settings_json_roundtrip(app, client):
    _login(client)
    app.config["WTF_CSRF_ENABLED"] = True
    token = _extract_csrf(client.get("/campaigns/new"))
    client.post(
        "/campaigns/new",
        data={
            "name": "Json",
            "type": "voice",
            "csrf_token": token,
        },
    )
    with client.application.app_context():
        campaign_id = Campaign.query.filter_by(name="Json").first().id

    token = _extract_csrf(client.get(f"/campaigns/{campaign_id}/edit"))
    resp = client.post(
        f"/campaigns/{campaign_id}/edit",
        data={
            "name": "Json",
            "type": "voice",
            "settings": '{"concurrent_calls": 20, "retry": 3}',
            "csrf_token": token,
        },
    )
    assert resp.status_code == 302
    with client.application.app_context():
        settings = Campaign.query.get(campaign_id).settings
        assert settings == {"concurrent_calls": 20, "retry": 3}
        assert isinstance(settings, dict)


def test_campaign_edit_invalid_settings_rejected(app, client):
    _login(client)
    app.config["WTF_CSRF_ENABLED"] = True
    token = _extract_csrf(client.get("/campaigns/new"))
    client.post(
        "/campaigns/new",
        data={
            "name": "BadJson",
            "type": "voice",
            "csrf_token": token,
        },
    )
    with client.application.app_context():
        campaign_id = Campaign.query.filter_by(name="BadJson").first().id

    token = _extract_csrf(client.get(f"/campaigns/{campaign_id}/edit"))
    resp = client.post(
        f"/campaigns/{campaign_id}/edit",
        data={
            "name": "BadJson",
            "type": "voice",
            "settings": "this is {not json",
            "csrf_token": token,
        },
    )
    # Invalid JSON re-renders the form with a flash instead of storing garbage.
    assert resp.status_code == 200
    with client.application.app_context():
        assert Campaign.query.get(campaign_id).settings == {}
