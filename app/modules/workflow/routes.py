from flask import jsonify, request
from flask_login import current_user, login_required

from app.extensions import db
from app.modules.workflow import workflow_bp
from app.modules.workflow.models import Event, Rule, Workflow
from app.modules.workflow.services import workflow_service


# Route handlers
@workflow_bp.route("/", methods=["GET"])
@login_required
def list_workflows():
    workflows = (
        Workflow.query.filter_by(created_by=current_user.id)
        .order_by(Workflow.created_at.desc())
        .all()
    )
    return jsonify([w.to_dict() for w in workflows])


@workflow_bp.route("/", methods=["POST"])
@login_required
def create_workflow():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    workflow = workflow_service.create_workflow(
        name=name,
        created_by=current_user.id,
        campaign_type=payload.get("campaign_type"),
        description=payload.get("description"),
        steps=payload.get("steps") or [],
    )
    return jsonify(workflow.to_dict()), 201


@workflow_bp.route("/<int:workflow_id>", methods=["GET"])
@login_required
def get_workflow(workflow_id):
    result = workflow_service.get_workflow_with_details(workflow_id)
    if not result:
        return jsonify({"error": "Workflow not found"}), 404
    return jsonify(result)


@workflow_bp.route("/<int:workflow_id>", methods=["PUT"])
@login_required
def update_workflow(workflow_id):
    workflow = Workflow.query.get(workflow_id)
    if not workflow:
        return jsonify({"error": "Workflow not found"}), 404

    if workflow.created_by != current_user.id and not current_user.has_permission(
        "edit_campaign"
    ):
        return jsonify({"error": "Unauthorized"}), 403

    payload = request.get_json(silent=True) or {}
    if "name" in payload:
        workflow.name = payload["name"].strip()
    if "campaign_type" in payload:
        workflow.campaign_type = payload["campaign_type"]
    if "description" in payload:
        workflow.description = payload["description"]
    if "steps" in payload:
        workflow.steps = payload["steps"]
    if "status" in payload:
        workflow.status = payload["status"]

    db.session.commit()
    return jsonify(workflow.to_dict())


@workflow_bp.route("/<int:workflow_id>", methods=["DELETE"])
@login_required
def delete_workflow(workflow_id):
    workflow = Workflow.query.get(workflow_id)
    if not workflow:
        return jsonify({"error": "Workflow not found"}), 404

    if workflow.created_by != current_user.id and not current_user.has_permission(
        "edit_campaign"
    ):
        return jsonify({"error": "Unauthorized"}), 403

    Rule.query.filter_by(workflow_id=workflow_id).delete()
    db.session.delete(workflow)
    db.session.commit()
    return jsonify({"status": "deleted"})


@workflow_bp.route("/<int:workflow_id>/rules", methods=["POST"])
@login_required
def add_rule(workflow_id):
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "name is required"}), 400

    workflow = Workflow.query.get(workflow_id)
    if not workflow:
        return jsonify({"error": "Workflow not found"}), 404

    if workflow.created_by != current_user.id and not current_user.has_permission(
        "edit_campaign"
    ):
        return jsonify({"error": "Unauthorized"}), 403

    rule = workflow_service.add_rule(
        workflow_id=workflow_id,
        name=data["name"],
        condition=data.get("condition"),
        action=data.get("action"),
        delay_seconds=data.get("delay_seconds", 0),
        max_retries=data.get("max_retries", 0),
        priority=data.get("priority", 100),
    )

    return jsonify(rule.to_dict()), 201


@workflow_bp.route("/execute", methods=["POST"])
@login_required
def execute_workflow_by_payload():
    """Execute a workflow identified in the JSON body: {'workflow_id': N}."""
    data = request.get_json()
    if not data or "workflow_id" not in data:
        return jsonify({"error": "workflow_id is required"}), 400

    result = workflow_service.execute_workflow(data["workflow_id"])
    if not result["success"]:
        return jsonify({"error": result["error"]}), 400

    return jsonify(result)


@workflow_bp.route("/<int:workflow_id>/execute", methods=["POST"])
@login_required
def execute_workflow():
    data = request.get_json()
    if not data or "workflow_id" not in data:
        return jsonify({"error": "workflow_id is required"}), 400

    workflow_id = data["workflow_id"]
    result = workflow_service.execute_workflow(workflow_id)
    if not result["success"]:
        return jsonify({"error": result["error"]}), 400

    return jsonify(result)


@workflow_bp.route("/events", methods=["GET"])
@login_required
def list_events():
    limit = request.args.get("limit", 100, type=int)
    events = Event.query.order_by(Event.timestamp.desc()).limit(limit).all()
    return jsonify([e.to_dict() for e in events])


@workflow_bp.route("/events/<int:event_id>", methods=["PUT"])
@login_required
def update_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    data = request.get_json(silent=True) or {}
    if "processed" in data:
        event.processed = data["processed"]
    if "data" in data:
        event.data = data["data"]

    db.session.commit()
    return jsonify(event.to_dict())


@workflow_bp.route("/events/cleanup", methods=["POST"])
@login_required
def cleanup_old_events():
    from datetime import datetime, timedelta

    cutoff_date = datetime.utcnow() - timedelta(days=30)
    Event.query.filter(Event.timestamp < cutoff_date).delete()
    db.session.commit()
    return jsonify({"status": "ok", "message": "Old events cleaned up"})
