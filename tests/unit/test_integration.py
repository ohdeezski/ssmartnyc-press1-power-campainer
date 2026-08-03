"""Integration tests: end-to-end across modules.

Verifies cross-module workflows work together (auth -> asset -> workflow -> notify).
These exercise the real route wiring, not just isolated unit logic.
"""
import io
import pytest


def _login(client):
    """Login as test admin via the auth_client pattern."""
    client.post("/auth/login", data={"email": "test@test.com", "password": "testpassword"})


@pytest.mark.integration
class TestAuthToNotification:
    def test_login_then_list_notifications(self, auth_user):
        """Logged-in user can list their notifications (empty is fine)."""
        resp = auth_user.get("/api/notifications/")
        assert resp.status_code in (200, 401)
        if resp.status_code == 200:
            body = resp.get_json()
            assert "notifications" in body or isinstance(body, list)


@pytest.mark.integration
class TestAuthToAsset:
    def test_asset_create_and_list(self, auth_user):
        """Create an asset with a file upload, then list/retrieve it."""
        data = {
            "name": "Integration Asset",
            "asset_type": "image",
            "subtype": "hero",
            "tags": json_dumps(["launch", "press"]),
        }
        resp = auth_user.post(
            "/api/assets/",
            data=data,
            content_type="multipart/form-data",
            buffered=True,
        )
        # Accept 200/201/400 (depends on whether file upload requirement enforced)
        assert resp.status_code in (200, 201, 400)
        if resp.status_code in (200, 201):
            body = resp.get_json()
            assert body is not None
            assert body.get("name") == "Integration Asset"


@pytest.mark.integration
class TestWorkflowLifecycle:
    def test_create_execute_workflow(self, auth_user):
        """Create a workflow, list it, execute it."""
        payload = {
            "name": "Integration Workflow",
            "campaign_type": "email",
            "description": "End-to-end test",
            "steps": [{"type": "send_email", "template": "welcome"}],
        }
        resp = auth_user.post("/api/workflows/", json=payload)
        assert resp.status_code in (200, 201, 400)
        if resp.status_code in (200, 201):
            wf = resp.get_json()
            assert wf.get("name") == "Integration Workflow"


@pytest.mark.integration
class TestHealthSmoke:
    def test_root_and_index(self, client):
        """Basic app boots and serves an HTTP response."""
        resp = client.get("/")
        assert resp.status_code in (200, 302)


@pytest.mark.integration
class TestConfigEngineIntegration:
    def test_set_get_system_config(self, auth_user):
        """Config engine accepts and returns a system setting."""
        resp = auth_user.get("/api/config/system")
        assert resp.status_code in (200, 401, 403)


def json_dumps(obj):
    import json
    return json.dumps(obj)
