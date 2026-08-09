"""Messaging pipeline backend — shared delivery path for Telegram/WhatsApp.

Delivers a campaign over the ``Message`` model (the dialer-side channel
table: sms|email|whatsapp) instead of ``Call`` rows. Subclasses implement
``_api_send`` with the provider HTTP call and mark :class:`Message`
status/sent_at/provider_message_id accordingly.
"""

from datetime import datetime, timezone

from app.extensions import db, socketio
from app.modules.dialer.backends.base import DialerBackend
from app.modules.dialer.models import Message


class MessagingBackend(DialerBackend):
    """Base for outbound message backends (Telegram/WhatsApp/sms)."""

    channel = "message"

    def __init__(self, config=None, **kwargs):
        self.config = config or {}

    # ------------------------------------------------------------------ #
    # body / destination resolution                                       #
    # ------------------------------------------------------------------ #
    def _resolve_body(self, settings):
        settings = settings or {}
        for key in (
            f"{self.channel}_template",
            "sms_template",
            "messaging_template",
            "template",
            "email_body",
        ):
            if settings.get(key):
                return settings[key]
        return ""

    def _destination_for(self, contact):
        """Resolve the delivery target (chat/personal id or phone)."""
        chat_id = getattr(contact, "chat_id", None) or getattr(
            contact, "telegram_id", None
        )
        if chat_id:
            return str(chat_id)
        phone = getattr(contact, "phone", None)
        if phone:
            return str(phone)
        return None

    # ------------------------------------------------------------------ #
    # DialerBackend interface                                             #
    # ------------------------------------------------------------------ #
    def health(self):
        import time

        start = time.time()
        try:
            ok = self._check()
        except Exception:  # noqa: BLE001 - probe surfaces as unhealthy
            ok = False
        latency = int((time.time() - start) * 1000)
        return {
            "status": "healthy" if ok else "unhealthy",
            "latency_ms": latency,
            "uptime": 1.0 if ok else 0.0,
            "mode": self.channel,
        }

    def launch(self, campaign_run, contacts):
        """Create Message rows and send them synchronously."""
        settings = campaign_run.settings_snapshot or {}
        body = self._resolve_body(settings)

        rows = []
        for contact in contacts or []:
            destination = self._destination_for(contact)
            if not destination:
                continue
            rows.append(
                Message(
                    campaign_run_id=campaign_run.id,
                    contact_phone=destination,
                    channel=self.channel,
                    status="queued",
                )
            )
        db.session.bulk_save_objects(rows)
        db.session.commit()

        sent, failed, skipped = 0, 0, 0
        for message in (
            Message.query.filter_by(
                campaign_run_id=campaign_run.id, channel=self.channel
            )
            .filter(Message.status == "queued")
            .all()
        ):
            if not body:
                message.status = "failed"
                failed += 1
                self._emit(message, False, "No template/body configured")
                continue
            try:
                ok, provider_id, error = self._api_send(body, message.contact_phone)
            except Exception as exc:  # noqa: BLE001 - provider may raise anything
                ok, provider_id, error = False, None, str(exc)

            if ok:
                message.status = "sent"
                message.sent_at = db.func.now()
                if provider_id:
                    message.provider_message_id = str(provider_id)
                sent += 1
            else:
                message.status = "failed"
                failed += 1
            self._emit(message, ok, error)
        db.session.commit()
        return {
            "created": len(rows),
            "sent": sent,
            "failed": failed,
            "skipped": skipped,
        }

    def tick(self, campaign_run):
        """Re-deliver any messages still queued."""
        settings = campaign_run.settings_snapshot or {}
        body = self._resolve_body(settings)
        pending = (
            Message.query.filter_by(
                campaign_run_id=campaign_run.id, channel=self.channel
            )
            .filter(Message.status == "queued")
            .all()
        )
        for message in pending:
            if not body:
                message.status = "failed"
                continue
            try:
                ok, provider_id, error = self._api_send(body, message.contact_phone)
            except Exception as exc:  # noqa: BLE001
                ok, provider_id, error = False, None, str(exc)
            if ok:
                message.status = "sent"
                message.sent_at = db.func.now()
                if provider_id:
                    message.provider_message_id = str(provider_id)
            else:
                message.status = "failed"
            self._emit(message, ok, error)
        db.session.commit()
        return {"processed": len(pending)}

    def pause(self, campaign_run):
        queued = Message.query.filter_by(
            campaign_run_id=campaign_run.id,
            channel=self.channel,
            status="queued",
        ).all()
        for message in queued:
            message.status = "paused"
        db.session.commit()

    def stop(self, campaign_run):
        queued = Message.query.filter_by(
            campaign_run_id=campaign_run.id,
            channel=self.channel,
            status="queued",
        ).all()
        for message in queued:
            message.status = "failed"
        db.session.commit()

    def status(self, campaign_run):
        messages = Message.query.filter_by(
            campaign_run_id=campaign_run.id, channel=self.channel
        ).all()
        counts = {}
        for m in messages:
            counts[m.status] = counts.get(m.status, 0) + 1
        return {
            "total_messages": len(messages),
            "status_counts": counts,
            "backend": self.channel,
        }

    # ------------------------------------------------------------------ #
    # helpers                                                             #
    # ------------------------------------------------------------------ #
    def _check(self):
        """Return True when the connector can reach the provider."""
        raise NotImplementedError

    def _api_send(self, body, destination, message=None):
        """Send one message. Returns (ok, provider_message_id, error)."""
        raise NotImplementedError

    def _emit(self, message, ok, error=None):
        socketio.emit(
            "campaign_event",
            {
                "run_id": message.campaign_run_id,
                "action": "message_sent" if ok else "message_failed",
                "message_id": message.id,
                "channel": self.channel,
                "contact_phone": message.contact_phone,
                "level": "info" if ok else "error",
                "error": error,
            },
            room=f"campaign:{message.campaign_run_id}",
            namespace="/",
        )


def _utcnow_iso():
    return datetime.now(timezone.utc).isoformat()
