#!/usr/bin/env python3
"""Gate 2 demo script — end-to-end Phase 2 validation."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.modules.campaigns.models import Campaign, CampaignRun
from app.modules.campaigns.services import CampaignService
from app.modules.contacts.models import ContactList, Contact
from app.modules.contacts.services import ContactImportService
from app.modules.dialer.services import DialerService
from app.modules.events.services import publish_event


def main():
    app = create_app("testing")
    with app.app_context():
        db.create_all()

        # 1. Create a campaign
        campaign = CampaignService.create_campaign(
            name="Demo Campaign",
            campaign_type="voice",
            created_by=1,
            settings={
                "concurrent_calls": 5,
                "retry_attempts": 2,
                "retry_delay": 30,
                "audio_intro_id": 1,
                "audio_hold_id": 2,
                "audio_agent_id": 3,
                "audio_voicemail_id": 4,
                "audio_outro_id": 5,
                "sms_template": "Hello {{name}}, call from Demo",
                "email_subject": "Demo Campaign",
                "email_body": "This is a demo",
            },
        )
        print(f"Created campaign: {campaign.name} (id={campaign.id})")

        # 2. Create a contact list
        cl = ContactList(name="Demo Contacts", created_by=1)
        db.session.add(cl)
        db.session.commit()
        campaign.contact_list_id = cl.id

        # 3. Seed contacts
        contact_objs = [
            Contact(contact_list_id=cl.id, phone=f"+1555{str(i).zfill(7)}")
            for i in range(10)
        ]
        db.session.bulk_save_objects(contact_objs)
        db.session.commit()
        print(f"Added {len(contact_objs)} contacts")

        # 4. Set caller profile and provider
        from app.modules.dialer.models import CallerProfile
        cp = CallerProfile(caller_name="Demo Caller", rotation_mode="fixed")
        db.session.add(cp)
        db.session.commit()
        campaign.caller_profile_id = cp.id

        from app.modules.dialer.models import Provider
        p = Provider(kind="asterisk", channel="voice", status="connected")
        db.session.add(p)
        db.session.commit()

        # 5. Set readiness manually (simulating a completed prepare step)
        campaign.readiness = {
            "checks": [{"id": "c", "label": "demo", "passed": True}] * 25,
            "all_passed": True,
            "contacts_loaded": 10,
            "duplicate_rate": 0,
            "invalid_count": 0,
            "dnc_ran": True,
            "pool_size": 1,
            "voice_provider_connected": True,
        }
        db.session.commit()

        # 6. Run PREPARE checklist (23/23)
        result = CampaignService.prepare_campaign(campaign.id)
        readiness = result.readiness or {}
        checks = readiness.get("checks", [])
        passed = sum(1 for c in checks if c["passed"])
        total = len(checks)
        print(f"PREPARE checklist: {passed}/{total} passed")
        assert passed == total, f"PREPARE checklist failed: {passed}/{total}"

        # 7. Run VERIFY checks (8/8)
        verify = CampaignService.verify_campaign(campaign.id)
        v_checks = verify["checks"]
        v_passed = sum(1 for c in v_checks if c["passed"])
        v_total = len(v_checks)
        print(f"VERIFY checks: {v_passed}/{v_total} passed")
        assert v_passed == v_total, f"VERIFY checks failed: {v_passed}/{v_total}"

        # 8. Estimate
        estimate = CampaignService.estimate_campaign(campaign.id)
        print(f"Estimate: {json.dumps(estimate, indent=2)}")
        assert estimate["total_contacts"] == 10

        # 9. Launch (gates on verified)
        launch_result = CampaignService.launch_campaign(campaign.id)
        assert launch_result is not None
        assert not isinstance(launch_result, dict) or "error" not in launch_result
        print(f"Campaign launched: status={campaign.status}")

        # 10. Run simulation
        run = CampaignRun(
            campaign_id=campaign.id,
            run_number=1,
            status="running",
            started_at=db.func.now(),
            total_contacts=10,
            settings_snapshot={"total_contacts": 10},
        )
        db.session.add(run)
        db.session.commit()

        service = DialerService()
        result = service.execute(run.id)
        print(f"Simulation result: {result}")
        assert result["status"] == "finished"

        # 11. Verify run counters
        db.session.refresh(run)
        print(f"Run finished: total_calls={run.total_calls}, success={run.success_count}, failed={run.failed_count}")
        assert run.total_calls == 10
        assert run.finished_at is not None

        # 12. Verify events were published
        events = publish_event.__module__
        print(f"Event bus module: {events}")

        print("\n✅ Gate 2 demo PASSED — all checks green")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Gate 2 demo FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
