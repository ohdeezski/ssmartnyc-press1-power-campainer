"""Tests for Asset Library module."""

import io

from app.extensions import db as _db
from app.modules.auth.models import User


def _upload_asset(client, name="Intro WAV", asset_type="audio", filename="intro.wav"):
    return client.post(
        "/api/assets/",
        data={
            "name": name,
            "type": asset_type,
            "file": (io.BytesIO(b"RIFF....data"), filename),
        },
        content_type="multipart/form-data",
    )


def test_list_assets_empty(auth_user):
    """Listing assets returns an empty page for a fresh account."""
    resp = auth_user.get("/api/assets/")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] == 0
    assert body["assets"] == []


def test_create_asset_multipart(auth_user):
    """Creating an asset from a multipart upload (not JSON) must work."""
    resp = _upload_asset(auth_user)
    assert resp.status_code == 201, resp.get_json()
    body = resp.get_json()
    assert body["name"] == "Intro WAV"
    assert body["type"] == "audio"
    assert body["file_id"] is not None


def test_get_asset(auth_user):
    created = _upload_asset(auth_user).get_json()
    resp = auth_user.get(f"/api/assets/{created['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Intro WAV"


def test_update_asset(auth_user):
    created = _upload_asset(auth_user).get_json()
    resp = auth_user.put(f"/api/assets/{created['id']}", json={"name": "New Name"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "New Name"


def test_delete_asset(auth_user):
    created = _upload_asset(auth_user).get_json()
    resp = auth_user.delete(f"/api/assets/{created['id']}")
    assert resp.status_code == 200
    resp = auth_user.get(f"/api/assets/{created['id']}")
    assert resp.status_code == 404


def test_search_assets(auth_user):
    _upload_asset(auth_user, name="Christmas Blast")
    resp = auth_user.get("/api/assets/search?q=christmas")
    assert resp.status_code == 200
    assert any(a["name"] == "Christmas Blast" for a in resp.get_json())


def test_asset_validation(auth_user):
    """Missing file must be rejected with 400, not crash."""
    resp = auth_user.post(
        "/api/assets/", data={"type": "audio"}, content_type="multipart/form-data"
    )
    assert resp.status_code == 400


def test_asset_permission_delete(auth_user, client):
    """A non-owner without manage_assets must not delete another user's asset."""
    created = _upload_asset(auth_user).get_json()
    with client.application.app_context():
        other = User(email="operator@test.com", name="Operator", role="operator")
        other.set_password("opassword")
        _db.session.add(other)
        _db.session.commit()
    # auth_user is still logged in as admin; switch to the operator first.
    client.get("/auth/logout")
    client.post(
        "/auth/login", data={"email": "operator@test.com", "password": "opassword"}
    )
    resp = client.delete(f"/api/assets/{created['id']}")
    assert resp.status_code == 403


def test_asset_file_handling_no_absolute_path(auth_user):
    """File metadata must not leak the absolute server path."""
    created = _upload_asset(auth_user).get_json()
    resp = auth_user.get(f"/api/assets/{created['id']}/file")
    assert resp.status_code == 200
    assert "file_path" not in resp.get_json()
