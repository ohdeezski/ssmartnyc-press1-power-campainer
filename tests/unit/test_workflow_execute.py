"""Workflow execution must record the run, emit events, and reach a terminal state."""

from app.extensions import db as _db
from app.modules.campaigns.models import Campaign


def test_execute_workflow_reaches_completed(auth_user):
    client = auth_user
    resp = client.post(
        "/api/workflows/", json={"name": "Flow", "campaign_type": "voice"}
    )
    assert resp.status_code == 201
    workflow_id = resp.get_json()["id"]

    resp = client.post(
        f"/api/workflows/{workflow_id}/rules",
        json={"workflow_id": workflow_id, "name": "Rule 1"},
    )
    assert resp.status_code == 201

    resp = client.post("/api/workflows/execute", json={"workflow_id": workflow_id})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["success"] is True
    assert body["campaign_id"]

    detail = client.get(f"/api/workflows/{workflow_id}").get_json()
    assert detail["workflow"]["status"] == "completed"
    assert detail["event_count"] >= 1

    with client.application.app_context():
        campaign = _db.session.get(Campaign, body["campaign_id"])
        assert campaign is not None
        # Honest status: nothing actually dialed yet.
        assert campaign.status == "draft"


def test_execute_workflow_twice_rejected(auth_user):
    client = auth_user
    resp = client.post("/api/workflows/", json={"name": "Once", "campaign_type": "sms"})
    workflow_id = resp.get_json()["id"]
    assert (
        client.post(
            "/api/workflows/execute", json={"workflow_id": workflow_id}
        ).status_code
        == 200
    )
    resp = client.post("/api/workflows/execute", json={"workflow_id": workflow_id})
    assert resp.status_code == 400
    assert "cannot be executed" in resp.get_json()["error"]


def test_execute_missing_workflow_rejected(auth_user):
    resp = auth_user.post("/api/workflows/execute", json={"workflow_id": 99999})
    assert resp.status_code == 400
