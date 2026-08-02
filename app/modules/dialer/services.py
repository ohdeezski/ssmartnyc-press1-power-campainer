from app.extensions import db, socketio
from app.modules.dialer.backends.simulation import SimulationBackend
from app.modules.dialer.models import Call


class DialerService:
    """Orchestrates dialer backends for campaign execution."""

    def __init__(self):
        self.backend = SimulationBackend(seed=42)

    def get_backend(self, backend_name=None):
        """Return the appropriate backend instance."""
        if backend_name == "asterisk":
            # Placeholder for real AsteriskBackend (Phase 4)
            raise NotImplementedError("AsteriskBackend not yet implemented")
        return self.backend

    def execute(self, campaign_run_id):
        """Run the full simulation for a campaign run."""
        from app.modules.campaigns.models import CampaignRun

        campaign_run = CampaignRun.query.get(campaign_run_id)
        if not campaign_run:
            return {"error": "CampaignRun not found"}

        # Get contacts for this campaign (simplified — uses campaign settings)
        contacts = self._get_contacts(campaign_run)

        # Launch
        self.backend.launch(campaign_run, contacts)
        socketio.emit("campaign_event", {
            "run_id": campaign_run_id,
            "action": "launched",
            "message": "Campaign simulation launched",
            "level": "info",
        }, room=f"campaign:{campaign_run_id}")

        # Tick until all calls are complete
        max_ticks = 200
        for tick_num in range(max_ticks):
            result = self.backend.tick(campaign_run)
            if result["processed"] == 0:
                break

            # Emit progress every 10 ticks
            if tick_num % 10 == 0:
                status = self.backend.status(campaign_run)
                socketio.emit("campaign_event", {
                    "run_id": campaign_run_id,
                    "action": "tick",
                    "tick": tick_num,
                    "status_counts": status["status_counts"],
                    "total_calls": status["total_calls"],
                    "level": "info",
                }, room=f"campaign:{campaign_run_id}")

        # Finalize
        self._finalize(campaign_run)
        return {"status": "finished", "run_id": campaign_run_id}

    def _get_contacts(self, campaign_run):
        """Get contacts for the campaign run (simplified)."""
        # In a real implementation, this would pull from ContactList
        # For simulation, generate synthetic contacts
        class FakeContact:
            def __init__(self, phone):
                self.phone = phone

        # Use campaign settings to determine contact count
        settings = campaign_run.settings_snapshot or {}
        total = settings.get("total_contacts", 100)
        return [FakeContact(f"+1555{str(i).zfill(7)}") for i in range(total)]

    def _finalize(self, campaign_run):
        """Mark campaign run as finished and update counters."""
        from app.modules.campaigns.models import CampaignRun

        calls = Call.query.filter_by(campaign_run_id=campaign_run.id).all()
        total = len(calls)
        answered = sum(1 for c in calls if c.outcome == "answered")
        press1 = sum(1 for c in calls if c.outcome == "press1")
        voicemail = sum(1 for c in calls if c.outcome == "voicemail")
        failed = sum(1 for c in calls if c.outcome in ("failed", "no_answer"))

        campaign_run.status = "finished"
        campaign_run.finished_at = db.func.now()
        campaign_run.total_calls = total
        campaign_run.success_count = answered
        campaign_run.failed_count = failed
        campaign_run.conversion_count = press1
        campaign_run.duration = 0
        db.session.commit()

        socketio.emit("campaign_event", {
            "run_id": campaign_run.id,
            "action": "finished",
            "counters": {
                "total": total,
                "answered": answered,
                "press1": press1,
                "voicemail": voicemail,
                "failed": failed,
            },
            "level": "success",
        }, room=f"campaign:{campaign_run.id}")

    def pause(self, campaign_run_id):
        from app.modules.campaigns.models import CampaignRun
        campaign_run = CampaignRun.query.get(campaign_run_id)
        self.backend.pause(campaign_run)
        socketio.emit(
            "campaign_event",
            {
                "run_id": campaign_run_id,
                "action": "paused",
                "level": "warning",
            },
            room=f"campaign:{campaign_run_id}",
        )

    def stop(self, campaign_run_id):
        from app.modules.campaigns.models import CampaignRun
        campaign_run = CampaignRun.query.get(campaign_run_id)
        self.backend.stop(campaign_run)
        socketio.emit(
            "campaign_event",
            {
                "run_id": campaign_run_id,
                "action": "stopped",
                "level": "error",
            },
            room=f"campaign:{campaign_run_id}",
        )
