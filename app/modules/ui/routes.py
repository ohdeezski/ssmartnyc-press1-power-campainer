from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.modules.auth.models import User
from app.modules.notifications.models import Notification
from app.modules.storage.models import StoredFile
from app.modules.ui import ui_bp


@ui_bp.route("/")
@login_required
def dashboard():
    from app.modules.campaigns.models import Campaign, CampaignRun
    from app.modules.workflow.models import Workflow
    from app.socket_events import collect_system_metrics

    total_files = StoredFile.query.count()
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id, read=False
    ).count()
    total_users = User.query.count()
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    active_campaigns = Campaign.query.filter(Campaign.status == "running").count()
    total_runs = CampaignRun.query.count()
    total_conversions = db.session.query(
        db.func.coalesce(db.func.sum(CampaignRun.conversion_count), 0)
    ).scalar()
    workflows = Workflow.query.count()

    # Real activity for the event feed — the operator's own notifications.
    recent_notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(8)
        .all()
    )
    type_color = {"success": "green", "warning": "yellow", "error": "red"}
    events = [
        {
            "time": n.created_at.strftime("%H:%M:%S") if n.created_at else "",
            "text": f"{n.title} — {n.message}",
            "color": type_color.get(n.type, "cyan"),
        }
        for n in recent_notifications
    ]
    return render_template(
        "ui/dashboard.html",
        total_files=total_files,
        unread_notifications=unread_notifications,
        total_users=total_users,
        active_campaigns=active_campaigns,
        total_campaigns=len(campaigns),
        total_runs=total_runs,
        total_conversions=total_conversions or 0,
        workflows=workflows,
        campaigns=campaigns,
        metrics=collect_system_metrics(),
        events=events,
        user=current_user,
    )


@ui_bp.route("/upload")
@login_required
def upload_center():
    from app.modules.assetlibrary.models import Asset

    recent_files = (
        StoredFile.query.order_by(StoredFile.created_at.desc()).limit(8).all()
    )
    recent_assets = Asset.query.order_by(Asset.created_at.desc()).limit(5).all()
    return render_template(
        "ui/upload_center.html",
        user=current_user,
        files=recent_files,
        assets=recent_assets,
        total_files=StoredFile.query.count(),
        total_assets=Asset.query.count(),
    )


@ui_bp.route("/providers")
@login_required
def provider_center():
    return render_template("ui/providers.html", user=current_user)


@ui_bp.route("/campaigns")
@login_required
def campaign_list():
    from app.modules.campaigns.models import Campaign

    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    return render_template("ui/campaigns.html", campaigns=campaigns, user=current_user)


@ui_bp.route("/settings")
@login_required
def settings_page():
    from app.modules.configengine.models import SystemConfig

    configs = SystemConfig.query.order_by(SystemConfig.category, SystemConfig.key).all()
    return render_template(
        "ui/settings.html",
        user=current_user,
        configs=configs,
        total_configs=len(configs),
        secret_count=sum(1 for c in configs if c.is_secret),
    )


@ui_bp.route("/notifications")
@login_required
def notifications_page():
    notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return render_template(
        "ui/notifications.html", notifications=notifications, user=current_user
    )


@ui_bp.route("/mission-control/<int:campaign_id>")
@login_required
def mission_control(campaign_id):
    from app.modules.campaigns.models import Campaign, CampaignRun
    from app.modules.dialer.models import Call

    campaign = Campaign.query.get_or_404(campaign_id)
    run = (
        CampaignRun.query.filter_by(campaign_id=campaign_id)
        .order_by(CampaignRun.run_number.desc())
        .first()
    )
    calls = None
    if run:
        calls = (
            Call.query.filter_by(campaign_run_id=run.id)
            .order_by(Call.created_at.desc())
            .limit(50)
            .all()
        )
    return render_template(
        "ui/mission_control.html",
        campaign=campaign,
        run=run,
        calls=calls,
        user=current_user,
    )


@ui_bp.route("/campaign-wizard/<int:campaign_id>", methods=["GET", "POST"])
@login_required
def campaign_wizard(campaign_id):
    from app.extensions import db
    from app.modules.campaigns.models import Campaign
    from app.modules.campaigns.services import (
        SENDER_FIELD_LABELS,
        _sender_clean,
        sender_identity,
    )
    from app.modules.contacts.models import ContactList

    campaign = Campaign.query.get_or_404(campaign_id)

    if request.method == "POST":
        # Step 1 “Prepare” saves the base campaign settings plus the
        # per-pipeline sender identity block. Redirect back to step 2
        # (Verify) so the operator can run readiness checks next.
        campaign.name = _sender_clean(request.form.get("name")) or campaign.name
        campaign.type = request.form.get("type") or campaign.type
        contact_list_id = request.form.get("contact_list_id")
        if contact_list_id:
            campaign.contact_list_id = int(contact_list_id)

        settings = dict(campaign.settings or {})
        # Keep legacy top-level call fields in sync when present.
        for key in ("concurrent_calls", "retry_attempts", "retry_delay"):
            value = request.form.get(key)
            if value == "" or value is None:
                continue
            try:
                settings[key] = int(value)
            except (TypeError, ValueError):
                continue

        sender = dict(campaign.settings.get("sender") or {})
        for field in SENDER_FIELD_LABELS:
            raw = request.form.get(field)
            if raw is not None:
                sender[field] = _sender_clean(raw)
        settings["sender"] = sender
        campaign.settings = settings
        db.session.commit()
        return redirect(url_for("ui.campaign_wizard", campaign_id=campaign.id, step=2))

    contact_lists = ContactList.query.order_by(ContactList.created_at.desc()).all()
    step = request.args.get("step", 1, type=int)
    readiness = campaign.readiness or {}
    return render_template(
        "ui/campaign_wizard.html",
        campaign=campaign,
        contact_lists=contact_lists,
        step=step,
        readiness=readiness if step > 1 else None,
        sender=sender_identity(campaign.settings),
        user=current_user,
    )


# Browsers probe /favicon.ico; point them at the SVG mark so there's no 404.
@ui_bp.route("/favicon.ico")
def favicon_ico():
    return redirect(url_for("static", filename="brand/favicon.svg"))
