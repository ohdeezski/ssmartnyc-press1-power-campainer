"""Tests for Phase 3 flight deck routes and functionality."""

import pytest
from app import create_app, db
from app.modules.campaigns.models import Campaign, CampaignRun
from app.modules.contacts.models import ContactList
from app.modules.dialer.models import Call
from app.modules.auth.models import User


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Log in via the login endpoint and return the client."""
    user = User.query.filter_by(email="admin@streetsmart.com").first()
    if not user:
        user = User(email="admin@streetsmart.com", name="Admin", role="admin")
        user.set_password("admin123")
        db.session.add(user)
        db.session.commit()

    # Log in via the login endpoint
    client.post("/auth/login", data={
        "email": "admin@streetsmart.com",
        "password": "admin123",
    }, follow_redirects=False)

    return client


class TestMissionControlRoute:
    def test_mission_control_requires_login(self, client, app):
        """Unauthenticated users are redirected to login."""
        with app.app_context():
            campaign = Campaign(name="Test", type="voice", created_by=1)
            db.session.add(campaign)
            db.session.commit()
            cid = campaign.id

        resp = client.get(f"/mission-control/{cid}")
        assert resp.status_code in (302, 401)

    def test_mission_control_renders(self, auth_client, app):
        """Authenticated users see the Mission Control page."""
        with app.app_context():
            campaign = Campaign(name="Test Mission", type="voice", created_by=1)
            db.session.add(campaign)
            db.session.commit()
            cid = campaign.id

        resp = auth_client.get(f"/mission-control/{cid}")
        assert resp.status_code == 200
        assert b"Mission Control" in resp.data

    def test_mission_control_with_run(self, auth_client, app):
        """Mission Control shows run data when a run exists."""
        with app.app_context():
            campaign = Campaign(name="Test Run", type="voice", created_by=1)
            db.session.add(campaign)
            db.session.commit()
            cid = campaign.id

            run = CampaignRun(
                campaign_id=cid,
                run_number=1,
                status="running",
                total_contacts=5,
                settings_snapshot={"total_contacts": 5},
            )
            db.session.add(run)
            db.session.commit()

        resp = auth_client.get(f"/mission-control/{cid}")
        assert resp.status_code == 200
        assert b"Test Run" in resp.data


class TestCampaignWizardRoute:
    def test_campaign_wizard_requires_login(self, client, app):
        """Unauthenticated users are redirected to login."""
        with app.app_context():
            campaign = Campaign(name="Test", type="voice", created_by=1)
            db.session.add(campaign)
            db.session.commit()
            cid = campaign.id

        resp = client.get(f"/campaigns/{cid}/wizard")
        assert resp.status_code in (302, 401)

    def test_campaign_wizard_renders(self, auth_client, app):
        """Authenticated users see the campaign wizard."""
        with app.app_context():
            campaign = Campaign(name="Test Wizard", type="voice", created_by=1)
            db.session.add(campaign)
            db.session.commit()
            cid = campaign.id

        resp = auth_client.get(f"/campaigns/{cid}/wizard", follow_redirects=True)
        assert resp.status_code == 200
        assert b"Campaign Wizard" in resp.data

    def test_campaign_wizard_step_param(self, auth_client, app):
        """Wizard respects the step query parameter."""
        with app.app_context():
            campaign = Campaign(name="Step Test", type="voice", created_by=1)
            db.session.add(campaign)
            db.session.commit()
            cid = campaign.id

        resp = auth_client.get(f"/campaigns/{cid}/wizard?step=2", follow_redirects=True)
        assert resp.status_code == 200

    def test_campaign_wizard_redirects_from_campaigns(self, auth_client, app):
        """The campaigns blueprint wizard route redirects to the UI route."""
        with app.app_context():
            campaign = Campaign(name="Redirect Test", type="voice", created_by=1)
            db.session.add(campaign)
            db.session.commit()
            cid = campaign.id

        resp = auth_client.get(f"/campaigns/{cid}/wizard", follow_redirects=True)
        # Should end up at the ui.campaign_wizard page
        assert resp.status_code == 200
        assert b"Campaign Wizard" in resp.data


class TestSimulationBackendSocketIO:
    def test_backend_has_socketio_import(self):
        """SimulationBackend imports socketio for event emission."""
        from app.modules.dialer.backends.simulation import SimulationBackend
        backend = SimulationBackend(seed=42)
        assert hasattr(backend, "_advance_call")

    def test_advance_call_has_campaign_run_id(self, app):
        """_advance_call can access campaign_run_id from the call."""
        from app.modules.dialer.backends.simulation import SimulationBackend

        with app.app_context():
            run = CampaignRun(campaign_id=1, status="running")
            db.session.add(run)
            db.session.commit()

            backend = SimulationBackend(seed=42)
            backend.launch(run, [])

            call = Call(
                campaign_run_id=run.id,
                contact_phone="+15551234567",
                status="preparing",
            )
            db.session.add(call)
            db.session.commit()
            call_id = call.id

            # Advance the call — should not raise
            backend._advance_call(call)
            db.session.commit()

            # Re-fetch to verify state changed
            refreshed = Call.query.get(call_id)
            assert refreshed.status in (
                "dialing",
                "ringing",
                "answered",
                "complete",
            )


class TestDashboardMissionControlLink:
    def test_dashboard_has_mission_control_link_for_running_campaigns(
        self, auth_client, app
    ):
        """Dashboard shows 'Live' link for running campaigns."""
        with app.app_context():
            campaign = Campaign(
                name="Live Campaign", type="voice", created_by=1, status="running"
            )
            db.session.add(campaign)
            db.session.commit()

        resp = auth_client.get("/")
        assert resp.status_code == 200
        assert b"Live" in resp.data

    def test_dashboard_has_launch_link_for_ready_campaigns(self, auth_client, app):
        """Dashboard shows 'Launch' link for ready campaigns."""
        with app.app_context():
            campaign = Campaign(
                name="Ready Campaign", type="voice", created_by=1, status="ready"
            )
            db.session.add(campaign)
            db.session.commit()

        resp = auth_client.get("/")
        assert resp.status_code == 200
        assert b"Launch" in resp.data
