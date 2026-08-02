"""Tests for the events module."""

import pytest

from app import create_app, db
from app.modules.events.models import AuditLog, Event
from app.modules.events.services import log_audit, publish_event


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


class TestPublishEvent:
    def test_publish_creates_event(self, app):
        event = publish_event(
            entity_type="campaign",
            entity_id=1,
            action="launched",
            message_human="Campaign launched",
            level="info",
        )
        assert event.id is not None
        assert event.action == "launched"
        assert event.level == "info"

    def test_publish_with_payload(self, app):
        event = publish_event(
            entity_type="campaign",
            entity_id=1,
            action="tick",
            payload={"count": 5},
        )
        assert event.payload == {"count": 5}


class TestAuditLog:
    def test_log_audit_creates_entry(self, app):
        entry = log_audit(
            user_id=1,
            action="create_campaign",
            entity_type="campaign",
            entity_id=42,
            details={"name": "Test"},
        )
        assert entry.id is not None
        assert entry.action == "create_campaign"
        assert entry.entity_id == 42


class TestEventModel:
    def test_event_to_dict(self, app):
        event = Event(
            entity_type="campaign",
            entity_id=1,
            action="launched",
            message_human="Campaign launched",
            level="info",
        )
        d = event.to_dict()
        assert d["action"] == "launched"
        assert d["level"] == "info"
        assert d["entity_type"] == "campaign"


class TestAuditLogModel:
    def test_audit_to_dict(self, app):
        log = AuditLog(
            user_id=1,
            action="test_action",
            entity_type="campaign",
            entity_id=1,
            details={"key": "value"},
        )
        d = log.to_dict()
        assert d["action"] == "test_action"
        assert d["details"] == {"key": "value"}
