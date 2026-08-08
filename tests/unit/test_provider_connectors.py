"""Tests for the messaging provider connectors (whatsapp/smtp/telegram)."""

from app.modules.providers.connectors.smtp import SMTPConnector
from app.modules.providers.connectors.telegram import TelegramConnector
from app.modules.providers.connectors.whatsapp import WhatsAppCloudConnector


class TestSMTPConnector:
    def test_missing_host_reports_disconnected(self):
        conn = SMTPConnector({})
        assert conn.connect() is False
        assert conn._connected is False

    def test_bad_credentials_reports_disconnected(self):
        conn = SMTPConnector(
            {
                "host": "smtp.invalid.test",
                "port": 587,
                "user": "u",
                "password": "p",
                "use_tls": False,
            }
        )
        # Host is unreachable in a sandbox without DNS; must not raise.
        assert conn.connect() is False

    def test_to_dict(self):
        conn = SMTPConnector({"host": "smtp.example.com"})
        data = conn.to_dict()
        assert data["kind"] == "smtp"
        assert data["channel"] == "email"
        assert data["status"] == "disconnected"


class TestWhatsAppConnector:
    def test_missing_credentials_reports_failed(self):
        conn = WhatsAppCloudConnector({})
        assert conn.connect() is False
        result = conn.test()
        assert result["status"] == "failed"
        assert "required" in result["message"]

    def test_valid_credentials_without_token(self):
        conn = WhatsAppCloudConnector({"token": "", "phone_number_id": ""})
        assert conn.connect() is False

    def test_present_credentials_connect(self):
        conn = WhatsAppCloudConnector({"token": "abc", "phone_number_id": "1234567890"})
        assert conn.connect() is True
        assert conn.to_dict()["status"] == "connected"


class TestTelegramConnector:
    def test_missing_token_reports_failed(self):
        conn = TelegramConnector({})
        assert conn.connect() is False
        result = conn.test()
        assert result["status"] == "failed"
        assert "token" in result["message"]

    def test_token_shape_connects(self):
        conn = TelegramConnector({"token": "123456:ABC-DEF"})
        assert conn.connect() is True

    def test_to_dict(self):
        conn = TelegramConnector({"token": "x"})
        data = conn.to_dict()
        assert data["kind"] == "telegram"
        assert data["channel"] == "messaging"
