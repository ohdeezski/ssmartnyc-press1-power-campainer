"""Twilio backend — Twilio Voice API wrapper for outbound dialing."""

import os
from datetime import datetime, timezone

from app.extensions import db, socketio
from app.modules.dialer.backends.base import DialerBackend
from app.modules.dialer.models import Call


class TwilioBackend(DialerBackend):
    """Twilio backend using the Twilio REST API for outbound calls."""

    def __init__(self, account_sid=None, auth_token=None, from_number=None):
        self.account_sid = account_sid or os.environ.get("TWILIO_ACCOUNT_SID", "")
        self.auth_token = auth_token or os.environ.get("TWILIO_AUTH_TOKEN", "")
        self.from_number = from_number or os.environ.get("TWILIO_FROM_NUMBER", "")
        self._client = None

    @property
    def client(self):
        """Lazily initialize the Twilio client."""
        if self._client is None:
            try:
                from twilio.rest import Client

                self._client = Client(self.account_sid, self.auth_token)
            except ImportError:
                raise ImportError(
                    "twilio package is required for TwilioBackend. "
                    "Install with: pip install twilio"
                )
        return self._client

    def health(self):
        """Check Twilio API connectivity."""
        import time

        start = time.time()
        try:
            # Verify credentials by listing calls
            self.client.calls.list(limit=1)
            latency = int((time.time() - start) * 1000)
            return {
                "status": "healthy",
                "latency_ms": latency,
                "uptime": 1.0,
                "mode": "twilio",
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "latency_ms": int((time.time() - start) * 1000),
                "uptime": 0.0,
                "mode": "twilio",
                "error": str(e),
            }

    def launch(self, campaign_run, contacts):
        """Create Call rows and initiate outbound calls via Twilio."""
        calls = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for contact in contacts:
            call = Call(
                campaign_run_id=campaign_run.id,
                contact_phone=(
                    contact.phone if hasattr(contact, "phone") else str(contact)
                ),
                status="preparing",
                status_history=[{"stage": "preparing", "timestamp": now_iso}],
            )
            calls.append(call)

        db.session.bulk_save_objects(calls)
        db.session.commit()

        # Initiate outbound calls via Twilio
        initiated = 0
        for call in calls:
            try:
                self._initiate_call(call, campaign_run)
                initiated += 1
            except Exception:
                call.status = "failed"
                call.finished_at = db.func.now()
                if call.status_history is None:
                    call.status_history = []
                call.status_history.append(
                    {
                        "stage": "failed",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

        db.session.commit()
        return {"created": len(calls), "initiated": initiated}

    def _initiate_call(self, call, campaign_run):
        """Place an outbound call via Twilio."""
        settings = campaign_run.settings_snapshot or {}
        twiml_url = settings.get("twiml_url", "")
        status_callback = settings.get("status_callback", "")

        params = {
            "to": call.contact_phone,
            "from_": self.from_number,
            "url": twiml_url or "",
        }
        if status_callback:
            params["status_callback"] = status_callback
            params["status_callback_event"] = [
                "initiated",
                "ringing",
                "answered",
                "completed",
            ]

        twilio_call = self.client.calls.create(**params)

        call.status = "dialing"
        call.call_uuid = twilio_call.sid
        if call.status_history is None:
            call.status_history = []
        call.status_history.append(
            {"stage": "dialing", "timestamp": datetime.now(timezone.utc).isoformat()}
        )
        db.session.commit()

        # Emit SocketIO event
        socketio.emit(
            "campaign_event",
            {
                "run_id": campaign_run.id,
                "action": "call_dialed",
                "call_id": call.id,
                "contact_phone": call.contact_phone,
                "twilio_call_sid": twilio_call.sid,
                "level": "info",
            },
            room=f"campaign:{campaign_run.id}",
            namespace="/",
        )

    def tick(self, campaign_run):
        """Check call statuses and update Call rows."""
        calls = (
            Call.query.filter_by(campaign_run_id=campaign_run.id)
            .filter(Call.status.in_(["preparing", "dialing", "ringing"]))
            .all()
        )

        for call in calls:
            self._check_call_status(call, campaign_run)

        db.session.commit()
        return {"processed": len(calls)}

    def _check_call_status(self, call, campaign_run):
        """Check the status of a Twilio call and update accordingly."""
        if not call.call_uuid:
            return

        try:
            twilio_call = self.client.calls(call.call_uuid).fetch()
            twilio_status = (
                twilio_call.status
            )  # queued, ringing, in-progress, completed, failed, busy, no-answer

            status_map = {
                "queued": "dialing",
                "ringing": "ringing",
                "in-progress": "answered",
                "completed": "complete",
                "failed": "failed",
                "busy": "failed",
                "no-answer": "no_answer",
            }

            new_status = status_map.get(twilio_status, twilio_status)

            if new_status != call.status:
                call.status = new_status
                if call.status_history is None:
                    call.status_history = []
                call.status_history.append(
                    {
                        "stage": new_status,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

                # Emit SocketIO event
                socketio.emit(
                    "campaign_event",
                    {
                        "run_id": campaign_run.id,
                        "action": "call_stage",
                        "call_id": call.id,
                        "contact_phone": call.contact_phone,
                        "stage": new_status,
                        "twilio_status": twilio_status,
                        "level": "info",
                    },
                    room=f"campaign:{campaign_run.id}",
                    namespace="/",
                )

                # Handle final outcomes
                if new_status == "complete":
                    call.outcome = "answered"
                    call.finished_at = db.func.now()
                elif new_status in ("failed", "busy", "no_answer"):
                    call.outcome = new_status
                    call.finished_at = db.func.now()
                    call.status = "complete"

        except Exception:
            pass

    def pause(self, campaign_run):
        """Pause all active calls."""
        calls = (
            Call.query.filter_by(campaign_run_id=campaign_run.id)
            .filter(Call.status.notin_(["complete", "failed", "blocked"]))
            .all()
        )
        for call in calls:
            call.status = "paused"
            if call.status_history is None:
                call.status_history = []
            call.status_history.append(
                {"stage": "paused", "timestamp": datetime.now(timezone.utc).isoformat()}
            )
        db.session.commit()

    def stop(self, campaign_run):
        """Stop all active calls."""
        calls = (
            Call.query.filter_by(campaign_run_id=campaign_run.id)
            .filter(Call.status.notin_(["complete", "failed", "blocked"]))
            .all()
        )
        for call in calls:
            call.status = "failed"
            call.finished_at = db.func.now()
            if call.status_history is None:
                call.status_history = []
            call.status_history.append(
                {"stage": "failed", "timestamp": datetime.now(timezone.utc).isoformat()}
            )
            # Cancel the Twilio call if it has a UUID
            if call.call_uuid:
                try:
                    self.client.calls(call.call_uuid).update(status="completed")
                except Exception:
                    pass
        db.session.commit()

    def status(self, campaign_run):
        """Return current status counts for the campaign run."""
        calls = Call.query.filter_by(campaign_run_id=campaign_run.id).all()
        status_counts = {}
        for call in calls:
            status_counts[call.status] = status_counts.get(call.status, 0) + 1
        return {
            "total_calls": len(calls),
            "status_counts": status_counts,
            "backend": "twilio",
        }
