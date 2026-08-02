from flask import jsonify, request
from flask_login import current_user, login_required

from app.extensions import db
from app.modules.dialer import dialer_bp
from app.modules.dialer.models import Call, CallerProfile
from app.modules.dialer.services import DialerService
from app.modules.providers.models import Provider


@dialer_bp.route("/providers", methods=["GET"])
@login_required
def list_providers():
    providers = Provider.query.all()
    return jsonify([p.to_dict() for p in providers])


@dialer_bp.route("/providers", methods=["POST"])
@login_required
def create_provider():
    data = request.get_json()
    if not data or not data.get("kind"):
        return jsonify({"error": "kind is required"}), 400
    provider = Provider(
        kind=data["kind"],
        channel=data.get("channel", "voice"),
        status=data.get("status", "disconnected"),
        priority=data.get("priority", 1),
        config=data.get("config", {}),
    )
    db.session.add(provider)
    db.session.commit()
    return jsonify(provider.to_dict()), 201


@dialer_bp.route("/providers/<int:provider_id>", methods=["GET"])
@login_required
def get_provider(provider_id):
    provider = Provider.query.get_or_404(provider_id)
    return jsonify(provider.to_dict())


@dialer_bp.route("/providers/<int:provider_id>/test", methods=["POST"])
@login_required
def test_provider(provider_id):
    provider = Provider.query.get_or_404(provider_id)
    # In simulation mode, always succeeds
    provider.status = "connected"
    provider.latency_ms = 1
    provider.last_health_check_at = db.func.now()
    db.session.commit()
    return jsonify({"status": "connected", "latency_ms": 1})


@dialer_bp.route("/caller-profiles", methods=["GET"])
@login_required
def list_caller_profiles():
    profiles = CallerProfile.query.all()
    return jsonify([p.to_dict() for p in profiles])


@dialer_bp.route("/caller-profiles", methods=["POST"])
@login_required
def create_caller_profile():
    data = request.get_json()
    if not data or not data.get("caller_name"):
        return jsonify({"error": "caller_name is required"}), 400
    profile = CallerProfile(
        caller_name=data["caller_name"],
        number=data.get("number"),
        sip_trunk=data.get("sip_trunk"),
        outbound_route=data.get("outbound_route"),
        caller_id_prefix=data.get("caller_id_prefix"),
        stir_shaken=data.get("stir_shaken", False),
        rotation_mode=data.get("rotation_mode", "fixed"),
    )
    db.session.add(profile)
    db.session.commit()
    return jsonify(profile.to_dict()), 201


@dialer_bp.route("/calls", methods=["GET"])
@login_required
def list_calls():
    run_id = request.args.get("run_id", type=int)
    if run_id:
        calls = Call.query.filter_by(campaign_run_id=run_id).all()
    else:
        calls = Call.query.all()
    return jsonify([c.to_dict() for c in calls])


@dialer_bp.route("/campaigns/<int:campaign_id>/launch", methods=["POST"])
@login_required
def launch_campaign(campaign_id):
    from app.modules.campaigns.models import Campaign, CampaignRun

    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.created_by != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    # Create a campaign run
    run = CampaignRun(
        campaign_id=campaign.id,
        run_number=1,
        status="running",
        started_at=db.func.now(),
        total_contacts=(
            campaign.settings.get("total_contacts", 100) if campaign.settings else 100
        ),
    )
    db.session.add(run)
    db.session.commit()

    # Start simulation in background (eager mode in dev)
    from app.modules.dialer.tasks import run_campaign

    run_campaign(run.id)

    return jsonify({"run_id": run.id, "status": "running"})


@dialer_bp.route("/campaigns/<int:campaign_id>/pause", methods=["POST"])
@login_required
def pause_campaign(campaign_id):
    service = DialerService()
    # Find the active run
    from app.modules.campaigns.models import CampaignRun

    run = CampaignRun.query.filter_by(campaign_id=campaign_id, status="running").first()
    if not run:
        return jsonify({"error": "No active run found"}), 404
    service.pause(run.id)
    return jsonify({"status": "paused"})


@dialer_bp.route("/campaigns/<int:campaign_id>/stop", methods=["POST"])
@login_required
def stop_campaign(campaign_id):
    service = DialerService()
    from app.modules.campaigns.models import CampaignRun

    run = CampaignRun.query.filter_by(campaign_id=campaign_id, status="running").first()
    if not run:
        return jsonify({"error": "No active run found"}), 404
    service.stop(run.id)
    return jsonify({"status": "stopped"})
