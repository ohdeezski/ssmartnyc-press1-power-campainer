"""Tests for the Craigslist reply integration."""

import smtplib

import pytest

from app.modules.campaigns.craigslist_integration import CraigslistReplyService


@pytest.fixture
def craigslist_config():
    return {
        "smtp_host": "smtp.example.com",
        "smtp_user": "relay-user",
        "smtp_password": "relay-pass",
        "from_email": "campaigns@street-smart.test",
        "from_name": "Street Smart Campaigns",
    }


def test_unconfigured_service_reports_not_configured():
    svc = CraigslistReplyService({})
    result = svc.send_reply(
        posting_id="12345",
        reply_content="Hello!",
        contact_info={"name": "Pat"},
    )
    assert result["status"] == "not_configured"
    assert "SMTP" in result["message"]


def test_empty_reply_reports_empty():
    svc = CraigslistReplyService({})
    result = svc.send_reply(
        posting_id="12345",
        reply_content="   ",
        contact_info={"name": "Pat"},
    )
    assert result["status"] == "empty"


def test_send_reply_failure_returns_failed(craigslist_config, monkeypatch):
    svc = CraigslistReplyService(craigslist_config)

    def boom(*_args, **_kwargs):
        raise smtplib.SMTPException("connection refused")

    monkeypatch.setattr(svc, "_send", boom)
    result = svc.send_reply(
        posting_id="12345",
        reply_content="Hello!",
        contact_info={"name": "Pat"},
    )
    assert result["status"] == "failed"
    assert "connection refused" in result["message"]


def test_send_reply_success_sets_sent(craigslist_config, monkeypatch):
    svc = CraigslistReplyService(craigslist_config)

    captured = {}

    def fake_send(msg):
        captured["message"] = msg

    monkeypatch.setattr(svc, "_send", fake_send)
    result = svc.send_reply(
        posting_id="12345",
        reply_content="Interested, tell me more.",
        contact_info={"name": "Pat", "email": "pat@example.com"},
        reply_email="anon123@reply.craigslist.org",
    )
    assert result["status"] == "sent"
    assert captured["message"]["To"] == "anon123@reply.craigslist.org"
    assert result["reply_to"] == "anon123@reply.craigslist.org"


def test_prepare_reply_substitutes_variables():
    svc = CraigslistReplyService({})
    content = svc.prepare_reply(
        "initial_reply",
        {
            "name": "Pat Smith",
            "post_topic": "Piano",
            "value_prop": "a reliable local buyer",
            "offer": "offering cash pickup today",
            "cta": "scheduling a viewing",
            "contact_name": "Alex",
            "contact_email": "alex@example.com",
        },
    )
    assert "Pat Smith" in content
    assert "Piano" in content
    assert "alex@example.com" in content


def test_configured_flag():
    assert CraigslistReplyService({}).configured is False
    assert (
        CraigslistReplyService(
            {
                "smtp_host": "smtp.example.com",
                "smtp_user": "u",
                "smtp_password": "p",
            }
        ).configured
        is True
    )
