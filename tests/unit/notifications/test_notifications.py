"""Tests for notifications module."""

from app.extensions import db as _db
from app.modules.auth.models import User
from app.modules.notifications.models import Notification
from app.modules.notifications.services import create_notification


def test_list_notifications_empty(auth_user):
    resp = auth_user.get("/api/notifications/")
    assert resp.status_code == 200
    assert resp.get_json() == []


def _toast(client, endpoint, message="Hello"):
    return client.post(
        f"/api/notifications/toast/{endpoint}", json={"message": message}
    )


def test_toast_notification_success(auth_user):
    resp = _toast(auth_user, "success")
    assert resp.status_code == 201
    assert resp.get_json()["message"] == "Hello"


def test_toast_notification_warning(auth_user):
    resp = _toast(auth_user, "warning")
    assert resp.status_code == 201
    assert resp.get_json()["type"] == "warning"


def test_toast_notification_error(auth_user):
    resp = _toast(auth_user, "error")
    assert resp.status_code == 201
    assert resp.get_json()["type"] == "error"


def test_toast_notification_info(auth_user):
    resp = _toast(auth_user, "info")
    assert resp.status_code == 201
    assert resp.get_json()["type"] == "info"


def test_mark_notification_read(auth_user):
    created = _toast(auth_user, "success").get_json()
    resp = auth_user.post(f"/api/notifications/{created['id']}/read")
    assert resp.status_code == 200
    with auth_user.application.app_context():
        assert _db.session.get(Notification, created["id"]).read is True


def test_mark_all_read(auth_user):
    _toast(auth_user, "success")
    _toast(auth_user, "warning")
    resp = auth_user.post("/api/notifications/read-all")
    assert resp.status_code == 200
    resp = auth_user.get("/api/notifications/")
    assert all(n["read"] for n in resp.get_json())


def test_mark_read_requires_owner(auth_user, client):
    """A different non-admin user must not mark another user's notification read."""
    with client.application.app_context():
        target = User(email="target@test.com", name="Target", role="viewer")
        target.set_password("tpassword")
        _db.session.add(target)
        _db.session.commit()
        other = User(email="other@test.com", name="Other", role="viewer")
        other.set_password("opassword")
        _db.session.add(other)
        _db.session.commit()
        note_id = create_notification(target.id, "info", "Title", "Message").id
    # auth_user is still logged in as admin; switch to the other user first.
    client.get("/auth/logout")
    client.post(
        "/auth/login", data={"email": "other@test.com", "password": "opassword"}
    )
    resp = client.post(f"/api/notifications/{note_id}/read")
    assert resp.status_code == 403


def test_admin_notification_creation(auth_user, test_admin_user):
    resp = auth_user.post(
        "/api/notifications/admin",
        json={
            "user_id": test_admin_user,
            "title": "Admin msg",
            "message": "hi",
        },
    )
    assert resp.status_code == 201
    assert resp.get_json()["user_id"] == test_admin_user


def test_admin_notification_requires_admin(auth_user, client):
    """Non-admin users must not create admin notifications."""
    with client.application.app_context():
        target = User(email="target2@test.com", name="Target", role="viewer")
        target.set_password("tpassword")
        _db.session.add(target)
        _db.session.commit()
        viewer = User(email="viewer@test.com", name="Viewer", role="viewer")
        viewer.set_password("vpassword")
        _db.session.add(viewer)
        _db.session.commit()
        target_id = target.id
    client.get("/auth/logout")
    client.post(
        "/auth/login", data={"email": "viewer@test.com", "password": "vpassword"}
    )
    resp = client.post(
        "/api/notifications/admin",
        json={
            "user_id": target_id,
            "title": "Admin msg",
            "message": "hi",
        },
    )
    assert resp.status_code == 403


def test_toast_notification_validation_error(auth_user):
    resp = auth_user.post("/api/notifications/toast/success", json={})
    assert resp.status_code == 400


def test_notification_model_to_dict(client):
    with client.application.app_context():
        user = User(email="model@test.com", name="Model", role="admin")
        user.set_password("mpassword")
        _db.session.add(user)
        _db.session.commit()
        n = create_notification(user.id, "info", "Title", "Message")
        d = n.to_dict()
        assert d["title"] == "Title"
        assert d["message"] == "Message"
        assert d["read"] is False
        assert d["type"] == "info"


def test_notification_created_at_format(client):
    with client.application.app_context():
        user = User(email="fmt@test.com", name="Fmt", role="admin")
        user.set_password("fpassword")
        _db.session.add(user)
        _db.session.commit()
        n = create_notification(user.id, "info", "Title", "Message")
        assert isinstance(n.to_dict()["created_at"], str)
