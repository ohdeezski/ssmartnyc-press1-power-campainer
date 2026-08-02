"""Smoke tests: every registered route must resolve and render.

These exist because a whole class of defects (missing templates, wrong
url_for endpoint names, unimported symbols) only surfaces at request time
and was invisible to the original two-test suite.
"""

import pytest
from flask import url_for

from app.extensions import db
from app.modules.auth.models import User


@pytest.fixture
def logged_in(client, app):
    with app.app_context():
        user = User(email="ops@example.com", name="Ops", role="admin")
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()
    client.post(
        "/auth/login",
        data={
            "email": "ops@example.com",
            "password": "testpassword123",
        },
        follow_redirects=True,
    )
    return client


def test_all_url_rules_build(app):
    """Catch url_for() BuildErrors for endpoints referenced in templates."""
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            if rule.endpoint == "static":
                continue
            sample = {arg: 1 for arg in rule.arguments}
            url_for(rule.endpoint, **sample)


@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/upload",
        "/providers",
        "/campaigns",
        "/settings",
        "/notifications",
    ],
)
def test_ui_pages_render(logged_in, path):
    resp = logged_in.get(path)
    assert resp.status_code == 200, f"{path} -> {resp.status_code}"


@pytest.mark.parametrize(
    "path",
    [
        "/campaigns/",
        "/campaigns/new",
    ],
)
def test_campaign_pages_render(logged_in, path):
    resp = logged_in.get(path)
    assert resp.status_code == 200, f"{path} -> {resp.status_code}"


def test_404_renders_error_template(client):
    # error handlers must not 500 themselves (missing errors/404.html)
    resp = client.get("/this-route-does-not-exist")
    assert resp.status_code == 404
    assert b"404" in resp.data


def test_health_endpoint_is_public(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "healthy"


@pytest.mark.parametrize(
    "path",
    [
        "/api/stats",
        "/api/files/",
        "/api/assets/",
        "/api/config/",
        "/api/notifications/",
        "/api/workflows/",
    ],
)
def test_api_endpoints_respond(logged_in, path):
    """Guards against NameError/AttributeError crashes (missing imports,
    missing to_dict) that return 500 instead of data."""
    resp = logged_in.get(path)
    assert resp.status_code in (200, 404), f"{path} -> {resp.status_code}"


@pytest.mark.parametrize("path", ["/", "/campaigns/", "/api/stats"])
def test_protected_routes_redirect_anonymous(client, path):
    resp = client.get(path)
    assert resp.status_code in (302, 401), f"{path} was not protected"
