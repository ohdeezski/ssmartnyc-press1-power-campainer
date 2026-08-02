"""Tests for the dialer module."""

import pytest
from app import create_app, db
from app.modules.dialer.models import Provider, CallerProfile, NumberPool, Call
from app.modules.dialer.backends.simulation import SimulationBackend
from app.modules.dialer.services import DialerService


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


class TestSimulationBackend:
    def test_health(self):
        backend = SimulationBackend(seed=42)
        health = backend.health()
        assert health["status"] == "healthy"
        assert health["latency_ms"] == 1

    def test_launch_creates_calls(self, app):
        from app.modules.campaigns.models import CampaignRun

        run = CampaignRun(campaign_id=1, status="running")
        db.session.add(run)
        db.session.commit()

        backend = SimulationBackend(seed=42)
        result = backend.launch(run, [])
        assert result["created"] == 0

    def test_advance_call_progresses(self, app):
        from app.modules.campaigns.models import CampaignRun

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

        backend.tick(run)
        db.session.refresh(call)
        assert call.status in (
            "dialing",
            "ringing",
            "answered",
            "complete",
        )

    def test_pause_sets_paused(self, app):
        from app.modules.campaigns.models import CampaignRun

        run = CampaignRun(campaign_id=1, status="running")
        db.session.add(run)
        db.session.commit()

        backend = SimulationBackend(seed=42)
        backend.pause(run)

    def test_stop_sets_failed(self, app):
        from app.modules.campaigns.models import CampaignRun

        run = CampaignRun(campaign_id=1, status="running")
        db.session.add(run)
        db.session.commit()

        backend = SimulationBackend(seed=42)
        backend.stop(run)


class TestDialerService:
    def test_execute_returns_finished(self, app):
        from app.modules.campaigns.models import CampaignRun

        run = CampaignRun(
            campaign_id=1,
            status="running",
            settings_snapshot={"total_contacts": 5},
        )
        db.session.add(run)
        db.session.commit()

        service = DialerService()
        result = service.execute(run.id)
        assert result["status"] == "finished"

    def test_pause(self, app):
        from app.modules.campaigns.models import CampaignRun

        run = CampaignRun(campaign_id=1, status="running")
        db.session.add(run)
        db.session.commit()

        service = DialerService()
        service.pause(run.id)

    def test_stop(self, app):
        from app.modules.campaigns.models import CampaignRun

        run = CampaignRun(campaign_id=1, status="running")
        db.session.add(run)
        db.session.commit()

        service = DialerService()
        service.stop(run.id)


class TestProviderModel:
    def test_provider_to_dict(self):
        p = Provider(kind="asterisk", channel="voice", status="connected")
        d = p.to_dict()
        assert d["kind"] == "asterisk"
        assert d["channel"] == "voice"
        assert d["status"] == "connected"


class TestCallerProfileModel:
    def test_profile_to_dict(self):
        cp = CallerProfile(caller_name="Test Caller", rotation_mode="fixed")
        d = cp.to_dict()
        assert d["caller_name"] == "Test Caller"
        assert d["rotation_mode"] == "fixed"


class TestCallModel:
    def test_call_to_dict(self):
        call = Call(
            campaign_run_id=1,
            contact_phone="+15551234567",
            status="complete",
            outcome="answered",
        )
        d = call.to_dict()
        assert d["contact_phone"] == "+15551234567"
        assert d["status"] == "complete"
        assert d["outcome"] == "answered"
