import random
from datetime import datetime, timezone

from app.extensions import db
from app.modules.dialer.backends.base import DialerBackend
from app.modules.dialer.models import Call


class SimulationBackend(DialerBackend):
    """Simulation backend for testing without real telecom infrastructure.

    Uses a seeded RNG so results are deterministic per campaign run.
    Simulates realistic call-stage timing (1-4s per stage) and outcome
    distributions (answer ~65%, press1 ~12% of answered, voicemail ~10%,
    no_answer ~15%, failed ~4%).
    """

    ANSWER_RATE = 0.65
    PRESS1_RATE = 0.12
    VOICEMAIL_RATE = 0.10
    NO_ANSWER_RATE = 0.15
    FAILED_RATE = 0.04
    STAGE_DELAYS = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0)

    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def health(self):
        return {"status": "healthy", "latency_ms": 1, "uptime": 1.0}

    def launch(self, campaign_run, contacts):
        """Create Call rows for all contacts in 'preparing' state."""
        calls = []
        now_iso = datetime.now(timezone.utc).isoformat()
        for contact in contacts:
            call = Call(
                campaign_run_id=campaign_run.id,
                contact_phone=contact.phone if hasattr(contact, "phone") else str(contact),
                status="preparing",
                status_history=[{"stage": "preparing", "timestamp": now_iso}],
            )
            calls.append(call)
        db.session.bulk_save_objects(calls)
        db.session.commit()
        return {"created": len(calls)}

    def tick(self, campaign_run):
        """Advance all 'preparing' or 'dialing' calls by one stage."""
        pending = (
            Call.query.filter_by(campaign_run_id=campaign_run.id)
            .filter(Call.status.in_(["preparing", "dialing", "ringing"]))
            .all()
        )
        for call in pending:
            self._advance_call(call)
        db.session.commit()
        return {"processed": len(pending)}

    def _advance_call(self, call):
        """Move a single call to the next stage."""
        stage_order = [
            "preparing",
            "dialing",
            "ringing",
            "answered",
            "playing_intro",
            "waiting",
            "press1",
            "transfer",
            "complete",
        ]
        current_idx = stage_order.index(call.status) if call.status in stage_order else 0
        next_idx = min(current_idx + 1, len(stage_order) - 1)
        next_stage = stage_order[next_idx]

        call.status = next_stage
        if call.status_history is None:
            call.status_history = []
        call.status_history.append(
            {"stage": next_stage, "timestamp": datetime.now(timezone.utc).isoformat()}
        )

        # Determine final outcome at the 'complete' stage
        if next_stage == "complete":
            roll = self.rng.random()
            if roll < self.ANSWER_RATE:
                call.outcome = "answered"
            elif roll < self.ANSWER_RATE + self.PRESS1_RATE:
                call.outcome = "press1"
                call.press1_detected = True
            elif roll < self.ANSWER_RATE + self.PRESS1_RATE + self.VOICEMAIL_RATE:
                call.outcome = "voicemail"
            elif roll < self.ANSWER_RATE + self.PRESS1_RATE + self.VOICEMAIL_RATE + self.NO_ANSWER_RATE:
                call.outcome = "no_answer"
            else:
                call.outcome = "failed"
            call.finished_at = db.func.now()

    def pause(self, campaign_run):
        # Simulation: just mark calls as paused
        calls = Call.query.filter_by(campaign_run_id=campaign_run.id).filter(
            Call.status.notin_(["complete", "failed", "blocked"])
        ).all()
        for call in calls:
            call.status = "paused"
        db.session.commit()

    def stop(self, campaign_run):
        calls = Call.query.filter_by(campaign_run_id=campaign_run.id).filter(
            Call.status.notin_(["complete", "failed", "blocked"])
        ).all()
        for call in calls:
            call.status = "failed"
            call.finished_at = db.func.now()
        db.session.commit()

    def status(self, campaign_run):
        calls = Call.query.filter_by(campaign_run_id=campaign_run.id).all()
        status_counts = {}
        for call in calls:
            status_counts[call.status] = status_counts.get(call.status, 0) + 1
        return {
            "total_calls": len(calls),
            "status_counts": status_counts,
            "backend": "simulation",
        }
