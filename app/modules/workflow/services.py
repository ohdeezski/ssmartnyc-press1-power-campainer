"""Workflow module service layer.

Extracted from routes.py (2026-08-02) to match the module pattern used by
every other module (campaigns, contacts, dialer, events, notifications,
configengine, assetlibrary, filemanager): routes thin, logic in services.py.

Spec reference: docs/version-1.0-spec.md L110-L114 (Workflow / Rule / Event).
"""

from app.extensions import db
from app.modules.campaigns.models import Campaign
from app.modules.notifications.services import send_success
from app.modules.workflow.models import Event, Rule, Workflow


class WorkflowService:
    """CRUD + execution logic for automation pipelines."""

    @staticmethod
    def create_workflow(
        name, created_by, campaign_type=None, description=None, steps=None
    ):
        workflow = Workflow(
            name=name,
            campaign_type=campaign_type,
            description=description,
            steps=steps or [],
            created_by=created_by,
        )
        db.session.add(workflow)
        db.session.commit()
        return workflow

    @staticmethod
    def add_rule(
        workflow_id,
        name,
        condition=None,
        action=None,
        delay_seconds=0,
        max_retries=0,
        priority=100,
    ):
        rule = Rule(
            workflow_id=workflow_id,
            name=name,
            condition=condition or {},
            action=action or {},
            delay_seconds=delay_seconds,
            max_retries=max_retries,
            priority=priority,
        )
        db.session.add(rule)
        db.session.commit()
        return rule

    @staticmethod
    def execute_workflow(workflow_id):
        workflow = Workflow.query.get(workflow_id)
        if not workflow or workflow.status != "draft":
            return {"success": False, "error": "Workflow cannot be executed"}

        # Create campaign run. Status is 'draft', not 'running': executing a
        # workflow merely stages a campaign — nothing has been dialed yet.
        campaign = Campaign(
            name=f"{workflow.name} Run - {workflow.created_at.strftime('%Y%m%d%H%M%S')}",
            type=workflow.campaign_type or "general",
            status="draft",
            created_by=workflow.created_by,
            workflow_id=workflow.id,
            settings={"workflow_steps": workflow.steps},
        )
        db.session.add(campaign)

        # Record a terminal event on the workflow event bus for each rule.
        rules = (
            Rule.query.filter_by(workflow_id=workflow.id).order_by(Rule.priority).all()
        )
        for rule in rules:
            db.session.add(
                Event(
                    event_type="workflow.rule",
                    entity_type="workflow",
                    entity_id=workflow.id,
                    data={
                        "rule": rule.name,
                        "rule_id": rule.id,
                        "priority": rule.priority,
                    },
                )
            )

        # Workflows reach a terminal state after a single execution.
        workflow.status = "completed"
        db.session.commit()

        # Send success notification
        send_success(
            workflow.created_by,
            f"Workflow '{workflow.name}' has been successfully executed",
        )

        return {
            "success": True,
            "workflow_id": workflow_id,
            "campaign_id": campaign.id,
            "message": f"Workflow '{workflow.name}' executed and campaign created",
        }

    @staticmethod
    def get_workflow_with_details(workflow_id):
        workflow = Workflow.query.get(workflow_id)
        if not workflow:
            return None

        return {
            "workflow": workflow.to_dict(),
            "rules": [
                rule.to_dict()
                for rule in Rule.query.filter_by(workflow_id=workflow_id)
                .order_by(Rule.priority)
                .all()
            ],
            "event_count": Event.query.filter_by(
                entity_type="workflow", entity_id=workflow_id
            ).count(),
        }


# Module-level singleton (routes import this, not the class).
workflow_service = WorkflowService()
