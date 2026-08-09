"""Tests for the Telegram and WhatsApp messaging delivery backends."""

import pytest

from app import create_app, db
from app.modules.dialer.backends.telegram import TelegramBackend
from app.modules.dialer.backends.whatsapp import WhatsAppBackend
from app.modules.dialer.models import Message, Provider


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def run(app):
    from app.modules.campaigns.models import CampaignRun

    r = CampaignRun(
        campaign_id=1,
        status="running",
        settings_snapshot={
            "telegram_template": "Hello from Telegram!",
            "whatsapp_template": "Hello from WhatsApp!",
        },
    )
    db.session.add(r)
    db.session.commit()
    return r


class _Resp:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


class FakeCont:
    """Scripted requests stand-in recording post/get calls."""

    def __init__(self):
        self.posts = []
        self.responses = []

    def _pop(self, default):
        return self.responses.pop(0) if self.responses else default

    def post(self, url, json=None, headers=None, timeout=None):
        self.posts.append({"url": url, "json": json, "headers": headers})
        payload = self._pop({"ok": True, "result": {"message_id": 424242}})
        return _Resp(payload, status_code=200)

    def get(self, url, params=None, headers=None, timeout=None):
        return _Resp(self._pop({"status_code": 200}), status_code=200)


class FakeResponses(FakeCont):
    def __init__(self, ok, description=None):
        super().__init__()
        payload = {"ok": ok, "result": {"message_id": 1}}
        if not ok:
            payload["description"] = description or "unauthorized"
        self.responses.append(payload)


class TestTelegramBackend:
    def test_health_without_token(self):
        assert TelegramBackend(config={}).health()["status"] == "unhealthy"

    def test_send_message_payload(self, monkeypatch):
        fake = FakeCont()
        monkeypatch.setattr("app.modules.dialer.backends.telegram.requests", fake)
        backend = TelegramBackend(config={"token": "123:abc"})
        ok, pid, err = backend._api_send("Hello!", "123456")
        assert ok is True
        assert pid == 424242
        assert fake.posts[0]["url"] == "https://api.telegram.org/bot123:abc/sendMessage"
        assert fake.posts[0]["json"]["chat_id"] == "123456"
        assert fake.posts[0]["json"]["text"] == "Hello!"

    def test_api_error_returns_reason(self, monkeypatch):
        fake = FakeCont()
        fake.responses.append({"ok": False, "description": "chat not found"})
        monkeypatch.setattr("app.modules.dialer.backends.telegram.requests", fake)
        backend = TelegramBackend(config={"token": "123:abc"})
        ok, pid, err = backend._api_send("hi", "999999")
        assert ok is False
        assert "chat not found" in err

    def test_launch_creates_and_sends(self, app, run, monkeypatch):
        monkeypatch.setattr("app.modules.dialer.backends.telegram.requests", FakeCont())
        backend = TelegramBackend(config={"token": "123:abc"})
        contacts = [type("C", (), {"chat_id": "111"})()]
        result = backend.launch(run, contacts)
        assert result["sent"] == 1
        msg = Message.query.filter_by(campaign_run_id=run.id).one()
        assert msg.channel == "telegram"
        assert msg.contact_phone == "111"
        assert msg.status == "sent"
        assert msg.provider_message_id == "424242"

    def test_status_counts(self, app, run, monkeypatch):
        monkeypatch.setattr("app.modules.dialer.backends.telegram.requests", FakeCont())
        backend = TelegramBackend(config={"token": "123:abc"})
        backend.launch(run, [type("C", (), {"chat_id": "222"})()])
        status = backend.status(run)
        assert status["total_messages"] == 1
        assert status["status_counts"]["sent"] == 1


class TestWhatsAppBackend:
    def test_send_message_payload(self, monkeypatch):
        fake = FakeCont()
        monkeypatch.setattr("app.modules.dialer.backends.whatsapp.requests", fake)
        backend = WhatsAppBackend(config={"token": "t", "phone_number_id": "55555"})
        ok, pid, err = backend._api_send("Hello WhatsApp", "+15550000000")
        assert ok is True
        call = fake.posts[0]
        assert "/55555/messages" in call["url"]
        assert call["headers"]["Authorization"] == "Bearer t"
        assert call["json"]["to"] == "+15550000000"
        assert call["json"]["text"]["body"] == "Hello WhatsApp"

    def test_health_without_creds(self):
        assert WhatsAppBackend(config={}).health()["status"] == "unhealthy"

    def test_launch_creates_message(self, app, run, monkeypatch):
        monkeypatch.setattr("app.modules.dialer.backends.whatsapp.requests", FakeCont())
        backend = WhatsAppBackend(config={"token": "t", "phone_number_id": "55"})
        contacts = [type("C", (), {"phone": "+15550000000"})()]
        result = backend.launch(run, contacts)
        assert result["sent"] == 1
        msg = Message.query.filter_by(campaign_run_id=run.id).one()
        assert msg.channel == "whatsapp"
        assert msg.status == "sent"


class TestDialerServiceBackendSelection:
    def test_telegram_provider(self, app):
        from app.modules.dialer.services import DialerService

        p = Provider(
            kind="telegram",
            channel="messaging",
            status="connected",
            config={"token": "123:abc"},
        )
        db.session.add(p)
        db.session.commit()
        backend = DialerService().get_backend(p)
        assert isinstance(backend, TelegramBackend)

    def test_whatsapp_provider(self, app):
        from app.modules.dialer.services import DialerService

        p = Provider(
            kind="whatsapp",
            channel="messaging",
            status="connected",
            config={"token": "t", "phone_number_id": "55"},
        )
        db.session.add(p)
        db.session.commit()
        backend = DialerService().get_backend(p)
        assert isinstance(backend, WhatsAppBackend)

    def test_messaging_finalize_counts_messages(self, app, run, monkeypatch):
        monkeypatch.setattr("app.modules.dialer.backends.telegram.requests", FakeCont())
        from app.modules.dialer.services import DialerService

        p = Provider(
            kind="telegram",
            channel="messaging",
            status="connected",
            config={"token": "123:abc"},
        )
        db.session.add(p)
        db.session.commit()
        svc = DialerService()
        provider = svc._get_provider_for_campaign(run)
        backend = svc.get_backend(provider)
        backend.launch(run, [type("C", (), {"chat_id": "999"})()])
        svc._finalize(run, backend)
        assert run.total_messages == 1
        assert run.success_count == 1
        assert run.total_calls == 0
