from app.extensions import db, socketio
from app.modules.dialer.backends.asterisk import AsteriskBackend
from app.modules.dialer.backends.simulation import SimulationBackend
from app.modules.dialer.backends.telegram import TelegramBackend
from app.modules.dialer.backends.twilio import TwilioBackend
from app.modules.dialer.backends.whatsapp import WhatsAppBackend
from app.modules.providers.models import Provider


class DialerService:
    """Orchestrates dialer backends for campaign execution."""

    BACKENDS = {
        "asterisk": AsteriskBackend,
        "twilio": TwilioBackend,
        "telegram": TelegramBackend,
        "whatsapp": WhatsAppBackend,
    }

    def __init__(self):
        self.backend = SimulationBackend(seed=42)

    def get_backend(self, provider=None):
        """Return the appropriate backend instance.

        If a Provider object is given, selects the backend based on
        provider.kind. Falls back to SimulationBackend.
        """
        if provider is None:
            return self.backend

        kind = getattr(provider, "kind", None)
        backend_class = self.BACKENDS.get(kind)

        if backend_class is None:
            return self.backend

        config = getattr(provider, "config", {}) or {}

        if kind == "asterisk":
            return backend_class(
                host=config.get("host"),
                port=config.get("port"),
                username=config.get("username"),
                secret=config.get("secret"),
                call_file_dir=config.get("call_file_dir"),
                context=config.get("context"),
                extension=config.get("extension"),
            )

        if kind == "twilio":
            return backend_class(
                account_sid=config.get("account_sid"),
                auth_token=config.get(
                    "auth_token"
                ),  # SECRET_GUARD_IGNORE: config key name, not a literal secret
                from_number=config.get("from_number"),
            )

        if kind in ("telegram", "whatsapp"):
            return backend_class(config=config)

        return self.backend

    def _get_provider_for_campaign(self, campaign_run):
        """Get the highest-priority connected provider for a campaign."""
        campaign = None
        try:
            from app.modules.campaigns.models import Campaign

            campaign = Campaign.query.get(campaign_run.campaign_id)
        except Exception:
            pass

        if campaign and campaign.provider_ids and len(campaign.provider_ids) > 0:
            return Provider.query.get(campaign.provider_ids[0])

        # Fall back to highest-priority connected provider
        return (
            Provider.query.filter_by(status="connected")
            .order_by(Provider.priority.asc())
            .first()
        )

    def execute(self, campaign_run_id):
        """Run the full campaign through the dialer backend."""
        from app.modules.campaigns.models import CampaignRun

        campaign_run = CampaignRun.query.get(campaign_run_id)
        if not campaign_run:
            return {"error": "CampaignRun not found"}

        # Get the provider for this campaign and its backend
        provider = self._get_provider_for_campaign(campaign_run)
        backend = self.get_backend(provider)

        # Get contacts for this campaign (simplified — uses campaign settings)
        contacts = self._get_contacts(campaign_run)

        # Create a CampaignRun if it doesn't exist (for backward compatibility)
        if campaign_run.status != "running":
            campaign_run.status = "running"
            campaign_run.started_at = db.func.now()
            db.session.commit()

        # Launch
        backend.launch(campaign_run, contacts)
        socketio.emit(
            "campaign_event",
            {
                "run_id": campaign_run_id,
                "action": "launched",
                "message": "Campaign launched",
                "level": "info",
            },
            room=f"campaign:{campaign_run_id}",
        )

        # Tick until all calls are complete
        max_ticks = 200
        for tick_num in range(max_ticks):
            result = backend.tick(campaign_run)
            if result["processed"] == 0:
                break

            # Emit progress every 10 ticks
            if tick_num % 10 == 0:
                status = backend.status(campaign_run)
                socketio.emit(
                    "campaign_event",
                    {
                        "run_id": campaign_run_id,
                        "action": "tick",
                        "tick": tick_num,
                        "status_counts": status["status_counts"],
                        "total_calls": status.get("total_calls", 0),
                        "total_messages": status.get("total_messages", 0),
                        "level": "info",
                    },
                    room=f"campaign:{campaign_run_id}",
                )

        # Finalize
        self._finalize(campaign_run, backend)
        return {"status": "finished", "run_id": campaign_run_id}

    def _get_contacts(self, campaign_run):
        """Get contacts for the campaign run.

        Uses the attached ContactList when one exists on the campaign
        (real names/phones), otherwise generates synthetic contacts to
        keep simulation/demo runs working.
        """
        campaign = None
        try:
            from app.modules.campaigns.models import Campaign

            campaign = Campaign.query.get(campaign_run.campaign_id)
        except Exception:
            pass

        if campaign and campaign.contact_list_id:
            from app.modules.contacts.models import Contact

            contacts = Contact.query.filter_by(
                contact_list_id=campaign.contact_list_id, status="ready"
            ).all()
            if contacts:
                return contacts

        # In a real implementation, this would pull from ContactList
        # For simulation, generate synthetic contacts
        class FakeContact:
            def __init__(self, phone):
                self.phone = phone

        # Use campaign settings to determine contact count
        settings = campaign_run.settings_snapshot or {}
        total = settings.get("total_contacts", 100)
        return [FakeContact(f"+1555{str(i).zfill(7)}") for i in range(total)]

    def _finalize(self, campaign_run, backend=None):
        """Mark campaign run as finished and update counters.

        Handles both call pipelines (``Call`` rows) and messaging
        pipelines (``Message`` rows) so campaign metrics stay correct
        whichever backend executed the run.
        """
        backend = backend or self.backend
        is_messaging = getattr(backend, "channel", None) in (
            "whatsapp",
            "telegram",
            "sms",
        )

        if is_messaging:
            from app.modules.dialer.models import Message

            messages = Message.query.filter_by(campaign_run_id=campaign_run.id).all()
            total = len(messages)
            sent = sum(1 for m in messages if m.status == "sent")
            failed = sum(1 for m in messages if m.status == "failed")
            paused = sum(1 for m in messages if m.status == "paused")

            campaign_run.status = "finished"
            campaign_run.finished_at = db.func.now()
            campaign_run.total_messages = total
            campaign_run.total_calls = 0
            campaign_run.success_count = sent
            campaign_run.failed_count = failed
            campaign_run.retry_count = paused
            campaign_run.duration = 0
            db.session.commit()

            socketio.emit(
                "campaign_event",
                {
                    "run_id": campaign_run.id,
                    "action": "finished",
                    "counters": {
                        "total_messages": total,
                        "sent": sent,
                        "failed": failed,
                    },
                    "level": "success",
                },
                room=f"campaign:{campaign_run.id}",
            )
            return

        from app.modules.dialer.models import Call

        calls = Call.query.filter_by(campaign_run_id=campaign_run.id).all()
        total = len(calls)
        answered = sum(1 for c in calls if c.outcome == "answered")
        press1 = sum(1 for c in calls if c.outcome == "press1")
        voicemail = sum(1 for c in calls if c.outcome == "voicemail")
        no_answer = sum(1 for c in calls if c.outcome == "no_answer")
        failed = sum(1 for c in calls if c.outcome in ("failed", "blocked"))

        campaign_run.status = "finished"
        campaign_run.finished_at = db.func.now()
        campaign_run.total_calls = total
        campaign_run.success_count = answered
        campaign_run.failed_count = failed
        campaign_run.conversion_count = press1
        campaign_run.voicemail_count = voicemail
        campaign_run.no_answer_count = no_answer
        campaign_run.retry_count = sum(1 for c in calls if c.attempt > 1)
        campaign_run.duration = 0
        db.session.commit()

        socketio.emit(
            "campaign_event",
            {
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
            },
            room=f"campaign:{campaign_run.id}",
        )

    def pause(self, campaign_run_id):
        from app.modules.campaigns.models import CampaignRun

        campaign_run = CampaignRun.query.get(campaign_run_id)
        provider = self._get_provider_for_campaign(campaign_run)
        backend = self.get_backend(provider)
        backend.pause(campaign_run)
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
        provider = self._get_provider_for_campaign(campaign_run)
        backend = self.get_backend(provider)
        backend.stop(campaign_run)
        socketio.emit(
            "campaign_event",
            {
                "run_id": campaign_run_id,
                "action": "stopped",
                "level": "error",
            },
            room=f"campaign:{campaign_run_id}",
        )
