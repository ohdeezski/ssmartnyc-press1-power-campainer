import json

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.modules.campaigns import campaigns_bp
from app.modules.campaigns.models import Campaign, CampaignRun


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
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.status = "running"
    campaign.started_at = db.func.now()
    db.session.commit()
    flash("Campaign launched", "success")
    return redirect(url_for("campaigns.campaign_detail", campaign_id=campaign.id))


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


@campaigns_bp.route("/<int:campaign_id>/report")
@login_required
def campaign_report(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template(
        "campaigns/report.html", campaign=campaign, user=current_user
    )
