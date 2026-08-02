import json

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.modules.campaigns import campaigns_bp
from app.modules.campaigns.models import Campaign, CampaignRun
from app.modules.campaigns.services import CampaignService


@campaigns_bp.route("/")
@login_required
def campaign_list():
    campaigns = Campaign.query.filter_by(created_by=current_user.id).all()
    return render_template(
        "campaigns/list.html", campaigns=campaigns, user=current_user
    )


@campaigns_bp.route("/new", methods=["GET", "POST"])
@login_required
def campaign_new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        campaign_type = request.form.get("type", "voice")
        if not name:
            flash("Campaign name is required", "danger")
            return render_template("campaigns/new.html", user=current_user)
        campaign = Campaign(name=name, type=campaign_type, created_by=current_user.id)
        db.session.add(campaign)
        db.session.commit()
        flash("Campaign created", "success")
        return redirect(url_for("campaigns.campaign_edit", campaign_id=campaign.id))
    return render_template("campaigns/new.html", user=current_user)


@campaigns_bp.route("/<int:campaign_id>/edit", methods=["GET", "POST"])
@login_required
def campaign_edit(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if request.method == "POST":
        campaign.name = request.form.get("name", campaign.name)
        campaign.type = request.form.get("type", campaign.type)
        settings_raw = request.form.get("settings", "")
        if settings_raw.strip():
            try:
                campaign.settings = json.loads(settings_raw)
            except (ValueError, TypeError):
                flash("Settings must be valid JSON", "danger")
                return render_template(
                    "campaigns/edit.html", campaign=campaign, user=current_user
                )
        else:
            campaign.settings = {}
        db.session.commit()
        flash("Campaign updated", "success")
        return redirect(url_for("campaigns.campaign_edit", campaign_id=campaign.id))
    return render_template("campaigns/edit.html", campaign=campaign, user=current_user)


@campaigns_bp.route("/<int:campaign_id>/launch", methods=["POST"])
@login_required
def campaign_launch(campaign_id):
    """Launch a campaign — checks verified_at via CampaignService, creates a
    CampaignRun, and kicks off the dialer.  Serves both the HTML form
    (mission_control / wizard) and the JSON API."""
    from app.modules.campaigns.services import CampaignService

    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.created_by != current_user.id:
        if request.path.startswith("/api"):
            return jsonify({"error": "Unauthorized"}), 403
        return redirect(url_for("campaigns.campaign_detail", campaign_id=campaign_id))

    # Delegate to CampaignService which gates on verified_at
    result = CampaignService.launch_campaign(campaign_id)
    if result is None:
        if request.path.startswith("/api"):
            return jsonify({"error": "Campaign not found"}), 404
        flash("Campaign not found", "danger")
        return redirect(url_for("campaigns.campaign_detail", campaign_id=campaign_id))
    if isinstance(result, dict) and "error" in result:
        # JSON API → JSON error
        return jsonify(result), 400

    campaign = result
    started = campaign.started_at.isoformat() if campaign.started_at else None

    # Create a CampaignRun and start the dialer backend
    from app.modules.campaigns.models import CampaignRun

    run = CampaignRun(
        campaign_id=campaign.id,
        run_number=1,
        status="running",
        started_at=db.func.now(),
        settings_snapshot=campaign.settings or {},
        total_contacts=(campaign.settings or {}).get("total_contacts", 100),
    )
    db.session.add(run)
    db.session.commit()

    # Start the dialer (eager-mode in dev via Celery, or direct for simulation)
    from app.modules.dialer.tasks import run_campaign

    run_campaign(run.id)

    # Content-negotiate: JSON client gets JSON, HTML form gets redirect to MC
    if request.accept_mimetypes.best == "application/json":
        return jsonify(
            {"status": campaign.status, "started_at": started, "run_id": run.id}
        )
    flash("Campaign launched", "success")
    return redirect(url_for("ui.mission_control", campaign_id=campaign.id))


@campaigns_bp.route("/<int:campaign_id>/pause", methods=["POST"])
@login_required
def campaign_pause(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.status = "paused"
    db.session.commit()
    flash("Campaign paused", "info")
    return redirect(url_for("campaigns.campaign_detail", campaign_id=campaign.id))


@campaigns_bp.route("/<int:campaign_id>/stop", methods=["POST"])
@login_required
def campaign_stop(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.status = "finished"
    campaign.finished_at = db.func.now()
    db.session.commit()
    flash("Campaign stopped", "info")
    return redirect(url_for("campaigns.campaign_detail", campaign_id=campaign.id))


@campaigns_bp.route("/<int:campaign_id>")
@login_required
def campaign_detail(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    runs = (
        CampaignRun.query.filter_by(campaign_id=campaign.id)
        .order_by(CampaignRun.run_number.desc())
        .all()
    )
    return render_template(
        "campaigns/detail.html", campaign=campaign, runs=runs, user=current_user
    )


@campaigns_bp.route("/<int:campaign_id>/wizard")
@login_required
def campaign_wizard(campaign_id):
    return redirect(url_for("ui.campaign_wizard", campaign_id=campaign_id))


@campaigns_bp.route("/<int:campaign_id>/report")
@login_required
def campaign_report(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template(
        "campaigns/report.html", campaign=campaign, user=current_user
    )


# JSON API endpoints
@campaigns_bp.route("/<int:campaign_id>/readiness", methods=["GET"])
@login_required
def campaign_readiness(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return jsonify(campaign.readiness or {})


@campaigns_bp.route("/<int:campaign_id>/verify", methods=["POST"])
@login_required
def campaign_verify(campaign_id):
    result = CampaignService.verify_campaign(campaign_id)
    if result is None:
        return jsonify({"error": "Campaign not found"}), 404
    return jsonify(result)


@campaigns_bp.route("/<int:campaign_id>/estimate", methods=["GET"])
@login_required
def campaign_estimate(campaign_id):
    result = CampaignService.estimate_campaign(campaign_id)
    if result is None:
        return jsonify({"error": "Campaign not found"}), 404
    return jsonify(result)


@campaigns_bp.route("/<int:campaign_id>/prepare", methods=["POST"])
@login_required
def campaign_prepare(campaign_id):
    campaign = CampaignService.prepare_campaign(campaign_id)
    if campaign is None:
        return jsonify({"error": "Campaign not found"}), 404
    return jsonify({"status": campaign.status, "readiness": campaign.readiness})


@campaigns_bp.route("/<int:campaign_id>/runs", methods=["GET"])
@login_required
def campaign_runs(campaign_id):
    runs = (
        CampaignRun.query.filter_by(campaign_id=campaign_id)
        .order_by(CampaignRun.run_number.desc())
        .all()
    )
    return jsonify([r.to_dict() for r in runs])
