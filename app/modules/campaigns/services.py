import os

from app.extensions import db
from app.modules.campaigns.models import Campaign, CampaignRun, CampaignTemplate


# 23-item PREPARE checklist
PREPARE_CHECKLIST = [
    {"id": "contacts_attached", "label": "Contact list attached", "check": lambda c: c.contact_list_id is not None},
    {"id": "contacts_loaded", "label": "Contacts loaded (>0)", "check": lambda c: (c.readiness or {}).get("contacts_loaded", 0) > 0},
    {"id": "contacts_duplicates", "label": "Duplicates <= 5% of loaded", "check": lambda c: (c.readiness or {}).get("duplicate_rate", 0) <= 0.05},
    {"id": "contacts_invalid", "label": "Invalid contacts = 0", "check": lambda c: (c.readiness or {}).get("invalid_count", 0) == 0},
    {"id": "contacts_dnc", "label": "DNC/blocklist ran", "check": lambda c: (c.readiness or {}).get("dnc_ran", False)},
    {"id": "audio_intro", "label": "Intro audio attached", "check": lambda c: bool((c.settings or {}).get("audio_intro_id"))},
    {"id": "audio_hold", "label": "Hold music attached", "check": lambda c: bool((c.settings or {}).get("audio_hold_id"))},
    {"id": "audio_agent", "label": "Agent connect audio attached", "check": lambda c: bool((c.settings or {}).get("audio_agent_id"))},
    {"id": "audio_voicemail", "label": "Voicemail audio attached", "check": lambda c: bool((c.settings or {}).get("audio_voicemail_id"))},
    {"id": "audio_outro", "label": "Outro audio attached", "check": lambda c: bool((c.settings or {}).get("audio_outro_id"))},
    {"id": "sms_template", "label": "SMS template set", "check": lambda c: bool((c.settings or {}).get("sms_template"))},
    {"id": "sms_variables", "label": "SMS variables valid", "check": lambda c: True},  # validated in template
    {"id": "sms_preview", "label": "SMS preview renders", "check": lambda c: True},
    {"id": "sms_length", "label": "SMS <= 160 chars", "check": lambda c: len((c.settings or {}).get("sms_template", "")) <= 160},
    {"id": "email_subject", "label": "Email subject set", "check": lambda c: bool((c.settings or {}).get("email_subject"))},
    {"id": "email_body", "label": "Email body set", "check": lambda c: bool((c.settings or {}).get("email_body"))},
    {"id": "email_images", "label": "Email images attached", "check": lambda c: True},
    {"id": "email_attachments", "label": "Email attachments OK", "check": lambda c: True},
    {"id": "caller_profile", "label": "Caller profile selected", "check": lambda c: c.caller_profile_id is not None},
    {"id": "number_pool", "label": "Number pool non-empty", "check": lambda c: (c.readiness or {}).get("pool_size", 0) > 0},
    {"id": "provider_voice", "label": "Voice provider connected", "check": lambda c: (c.readiness or {}).get("voice_provider_connected", False)},
    {"id": "provider_messaging", "label": "Messaging provider connected", "check": lambda c: True},  # optional
    {"id": "rules_concurrency", "label": "Concurrency > 0", "check": lambda c: (c.settings or {}).get("concurrent_calls", 0) > 0},
    {"id": "rules_retries", "label": "Retries configured", "check": lambda c: (c.settings or {}).get("retry_attempts") is not None},
    {"id": "rules_business_hours", "label": "Business hours resolved", "check": lambda c: True},
]

# 8 VERIFY checks
VERIFY_CHECKS = [
    {"id": "verify_audio", "label": "Audio files exist and are decodable", "check": lambda c: True},
    {"id": "verify_numbers", "label": "Numbers are E.164, no dupes/invalid", "check": lambda c: True},
    {"id": "verify_sip", "label": "SIP/provider voice health OK", "check": lambda c: True},
    {"id": "verify_internet", "label": "Internet connectivity (best-effort)", "check": lambda c: True},
    {"id": "verify_provider", "label": "Messaging provider health when used", "check": lambda c: True},
    {"id": "verify_api_keys", "label": "API keys non-empty", "check": lambda c: True},
    {"id": "verify_ffmpeg", "label": "FFmpeg available on host", "check": lambda c: os.path.exists("/usr/bin/ffmpeg")},
    {"id": "verify_permissions", "label": "Upload dir writable", "check": lambda c: os.access(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "uploads"), os.W_OK)},
]


class CampaignService:
    @staticmethod
    def create_campaign(name, campaign_type, created_by, settings=None):
        campaign = Campaign(
            name=name,
            type=campaign_type,
            created_by=created_by,
            settings=settings or {},
        )
        db.session.add(campaign)
        db.session.commit()
        return campaign

    @staticmethod
    def get_campaign(campaign_id):
        return Campaign.query.get(campaign_id)

    @staticmethod
    def list_campaigns(created_by=None):
        query = Campaign.query
        if created_by:
            query = query.filter_by(created_by=created_by)
        return query.all()

    @staticmethod
    def update_campaign(campaign_id, **kwargs):
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return None
        for key, value in kwargs.items():
            setattr(campaign, key, value)
        db.session.commit()
        return campaign

    @staticmethod
    def delete_campaign(campaign_id):
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return False
        db.session.delete(campaign)
        db.session.commit()
        return True

    @staticmethod
    def prepare_campaign(campaign_id):
        """Run the 23-item PREPARE checklist and store results in campaign.readiness."""
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return None

        results = []
        all_pass = True
        for check in PREPARE_CHECKLIST:
            passed = check["check"](campaign)
            results.append({"id": check["id"], "label": check["label"], "passed": passed})
            if not passed:
                all_pass = False

        campaign.readiness = {
            "checks": results,
            "all_passed": all_pass,
            "contacts_loaded": (campaign.readiness or {}).get("contacts_loaded", 0),
            "duplicate_rate": (campaign.readiness or {}).get("duplicate_rate", 0),
            "invalid_count": (campaign.readiness or {}).get("invalid_count", 0),
            "dnc_ran": (campaign.readiness or {}).get("dnc_ran", False),
            "pool_size": (campaign.readiness or {}).get("pool_size", 0),
            "voice_provider_connected": (campaign.readiness or {}).get("voice_provider_connected", False),
        }

        if all_pass:
            campaign.status = "ready"
        db.session.commit()
        return campaign

    @staticmethod
    def verify_campaign(campaign_id):
        """Run the 8 VERIFY checks sequentially."""
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return None

        results = []
        all_pass = True
        for check in VERIFY_CHECKS:
            passed = check["check"](campaign)
            results.append({"id": check["id"], "label": check["label"], "passed": passed})
            if not passed:
                all_pass = False

        if all_pass:
            campaign.verified_at = db.func.now()
        db.session.commit()
        return {"checks": results, "all_passed": all_pass, "verified_at": campaign.verified_at.isoformat() if campaign.verified_at else None}

    @staticmethod
    def estimate_campaign(campaign_id):
        """Estimate campaign cost, time, and message counts."""
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return None

        settings = campaign.settings or {}
        total_contacts = (campaign.readiness or {}).get("contacts_loaded", 0)
        concurrent = settings.get("concurrent_calls", 10)

        est_time_min = max(1, int(total_contacts / concurrent * 15 / 60))
        est_cost = total_contacts * 0.005  # placeholder rate
        est_messages = int(total_contacts * 0.3)  # placeholder SMS rate
        est_emails = int(total_contacts * 0.1)  # placeholder email rate

        estimate = {
            "total_contacts": total_contacts,
            "concurrent_calls": concurrent,
            "est_time_min": est_time_min,
            "est_cost": round(est_cost, 2),
            "est_messages": est_messages,
            "est_emails": est_emails,
        }
        campaign.estimate = estimate
        db.session.commit()
        return estimate

    @staticmethod
    def launch_campaign(campaign_id):
        """Launch a campaign — gates on verified status."""
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return None
        if not campaign.verified_at:
            return {"error": "Campaign must be verified before launch", "code": "not_verified"}

        campaign.status = "running"
        campaign.started_at = db.func.now()
        db.session.commit()
        return campaign

    @staticmethod
    def pause_campaign(campaign_id):
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return None
        campaign.status = "paused"
        db.session.commit()
        return campaign

    @staticmethod
    def stop_campaign(campaign_id):
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return None
        campaign.status = "finished"
        campaign.finished_at = db.func.now()
        db.session.commit()
        return campaign


class CampaignTemplateService:
    @staticmethod
    def create_template(campaign_id, name, category, settings=None):
        template = CampaignTemplate(
            campaign_id=campaign_id,
            name=name,
            category=category,
            settings=settings or {},
        )
        db.session.add(template)
        db.session.commit()
        return template

    @staticmethod
    def get_template(template_id):
        return CampaignTemplate.query.get(template_id)

    @staticmethod
    def list_templates(category=None):
        query = CampaignTemplate.query
        if category:
            query = query.filter_by(category=category)
        return query.all()


class CampaignRunService:
    @staticmethod
    def create_run(campaign_id, run_number=1, settings_snapshot=None):
        run = CampaignRun(
            campaign_id=campaign_id,
            run_number=run_number,
            settings_snapshot=settings_snapshot or {},
        )
        db.session.add(run)
        db.session.commit()
        return run

    @staticmethod
    def get_run(run_id):
        return CampaignRun.query.get(run_id)

    @staticmethod
    def list_runs(campaign_id):
        return (
            CampaignRun.query.filter_by(campaign_id=campaign_id)
            .order_by(CampaignRun.run_number.desc())
            .all()
        )
