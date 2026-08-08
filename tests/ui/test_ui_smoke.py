"""UI smoke tests: every authenticated page renders 200."""

import pytest

from app.extensions import db
from app.modules.auth.models import User


@pytest.fixture
def ui_user(client):
    """Logged-in admin client for UI pages."""
    with client.application.app_context():
        user = User(email="ui@example.com", name="UI", role="admin")
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()
    client.post(
        "/auth/login",
        data={"email": "ui@example.com", "password": "testpassword123"},
        follow_redirects=True,
    )
    return client


PAGES = [
    "/",
    "/upload",
    "/providers",
    "/campaigns",
    "/settings",
    "/notifications",
]


@pytest.mark.parametrize("path", PAGES)
def test_ui_pages_render(ui_user, path):
    resp = ui_user.get(path)
    assert resp.status_code == 200, f"{path} returned {resp.status_code}"


def test_dashboard_has_title(ui_user):
    resp = ui_user.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "<title>" in html


def test_favicon_resolves(client):
    resp = client.get("/favicon.ico")
    assert resp.status_code == 302


def test_unauthenticated_ui_redirects_to_login(client):
    resp = client.get("/")
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]
