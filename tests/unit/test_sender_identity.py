"""Per-campaign sender identity: persistence + dialer/smtp consumption."""

import pytest

from app import create_app, db
from app.modules.campaigns.services import SENDER_FIELD_LABELS, sender_identity
from app.modules.dialer.backends.asterisk import AsteriskBackend


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def user(app):
    from app.modules.auth.models import User

    u = User(email="c@example.com", name="C", role="admin")
    u.set_password("pw123456")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def campaign(app, user):
    from app.modules.campaigns.models import Campaign

    c = Campaign(name="Sender Test", type="voice", created_by=user.id)
    db.session.add(c)
    db.session.commit()
    return c


class TestSenderIdentityResolver:
    def test_fills_all_fields_none_default(self):
        out = sender_identity({})
        assert set(out) == set(SENDER_FIELD_LABELS)
        assert all(v is None for v in out.values())

    def test_reads_nested_sender_block(self):
        out = sender_identity(
            {
                "sender": {
                    "caller_id_name": "LES Bar",
                    "caller_id_number": "+12125550100",
                }
            }
        )
        assert out["caller_id_name"] == "LES Bar"
        assert out["caller_id_number"] == "+12125550100"

    def test_legacy_top_level_caller_id_shim(self):
        out = sender_identity(
            {"caller_id": "Old Co", "caller_id_number": "+15550000001"}
        )
        assert out["caller_id_name"] == "Old Co"
        assert out["caller_id_number"] == "+15550000001"


class TestWizardPersistence:
    def _login(self, client):
        client.post(
            "/auth/login",
            data={"email": "c@example.com", "password": "pw123456"},
        )

    def test_wizard_step1_saves_sender(self, app, campaign, user):
        client = app.test_client()
        self._login(client)
        resp = client.post(
            f"/campaign-wizard/{campaign.id}",
            data={
                "name": "Sender Test",
                "type": "email",
                "concurrent_calls": "7",
                "caller_id_name": "LES Bar",
                "caller_id_number": "+12125550100",
                "email_from_name": "LES Bar",
                "email_from_address": "hello@lesbar.com",
            },
        )
        assert resp.status_code == 302
        db.session.expire_all()
        settings = campaign.settings
        assert settings["concurrent_calls"] == 7
        assert settings["sender"]["caller_id_name"] == "LES Bar"
        assert settings["sender"]["email_from_address"] == "hello@lesbar.com"


class TestAsteriskBackendConsumesSender:
    def test_sender_identity_in_written_file(self, app, tmp_path):
        from app.modules.campaigns.models import CampaignRun
        from app.modules.dialer.models import Call

        run = CampaignRun(campaign_id=999)
        run.settings_snapshot = {
            "sender": {"caller_id_number": "+17725550199", "caller_id_name": "BrandX"}
        }
        db.session.add(run)
        db.session.commit()
        assert run.id is not None
        call = Call(id=7, contact_phone="+15552223333")
        backend = AsteriskBackend(call_file_dir=str(tmp_path))
        written = backend._write_call_file(call, run)
        assert written is True
        content = (tmp_path / f"call_{run.id}_7.call").read_text()
        assert "+17725550199" in content
        assert "BrandX" in content
        assert 'Set: CALLERID(all)="BrandX"<+17725550199>' in content
        # The recipient's own number must never appear as the caller identity.
        assert "+15552223333" not in content.split("Set: CALLERID(all)=")[-1]

    def test_legacy_caller_id_used_as_fallback(self, app, tmp_path):
        from app.modules.campaigns.models import CampaignRun
        from app.modules.dialer.models import Call

        run = CampaignRun(campaign_id=1000)
        run.settings_snapshot = {"caller_id": "Old Co"}
        db.session.add(run)
        db.session.commit()
        call = Call(id=1, contact_phone="+15550000000")
        backend = AsteriskBackend(call_file_dir=str(tmp_path))
        assert backend._write_call_file(call, run) is True
        content = (tmp_path / f"call_{run.id}_1.call").read_text()
        assert "Old Co" in content


class TestSMPSenderOverride:
    def test_send_reply_uses_sender_identity(self, app, monkeypatch):
        from app.modules.campaigns.craigslist_integration import CraigslistReplyService

        svc = CraigslistReplyService(
            config={
                "smtp_host": "smtp.example.com",
                "smtp_user": "u",
                "smtp_password": "p",
                "from_name": "Default Name",
                "from_email": "default@example.com",
            }
        )
        sent = {}

        class FakeServer:
            def __init__(self, *a, **k):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def starttls(self):
                pass

            def login(self, *a):
                pass

            def send_message(self, msg):
                sent["from"] = msg["From"]
                sent["subject"] = msg["Subject"]

            def quit(self):
                pass

        class FakeModule:
            def SMTP(self, *a, **k):
                return FakeServer()

        monkeypatch.setattr(
            "app.modules.campaigns.craigslist_integration.smtplib", FakeModule()
        )
        res = svc.send_reply(
            "123400",
            "hello",
            {"name": "x"},
            sender_identity={
                "email_from_name": "Campaign Brand",
                "email_from_address": "campaign@brand.com",
            },
        )
        assert res["status"] == "sent"
        assert "Campaign Brand" in sent["from"]
        assert "campaign@brand.com" in sent["from"]

    def test_default_from_used_when_no_override(self, app, monkeypatch):
        from app.modules.campaigns.craigslist_integration import CraigslistReplyService

        svc = CraigslistReplyService(
            config={
                "smtp_host": "smtp.example.com",
                "smtp_user": "u",
                "smtp_password": "p",
                "from_name": "Default Name",
                "from_email": "default@example.com",
            }
        )
        sent = {}

        class FakeServer:
            def __init__(self, *a, **k):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def starttls(self):
                pass

            def login(self, *a):
                pass

            def send_message(self, msg):
                sent["from"] = msg["From"]

            def quit(self):
                pass

        class FakeModule:
            def SMTP(self, *a, **k):
                return FakeServer()

        monkeypatch.setattr(
            "app.modules.campaigns.craigslist_integration.smtplib", FakeModule()
        )
        svc.send_reply("1", "hi", {})
        assert "Default Name" in sent["from"]
        assert "default@example.com" in sent["from"]
