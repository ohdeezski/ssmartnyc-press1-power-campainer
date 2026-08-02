"""0001 baseline

Revision ID: 22a231c03925
Revises: None
Create Date: 2026-08-02 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "22a231c03925"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(512), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, default="viewer"),
        sa.Column("status", sa.String(50), nullable=False, default="active"),
        sa.Column("mfa_enabled", sa.Boolean(), default=False),
        sa.Column("mfa_secret", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("last_login_ip", sa.String(45)),
    )
    op.create_table(
        "stored_files",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("original_name", sa.String(500), nullable=False),
        sa.Column("stored_name", sa.String(500), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("subcategory", sa.String(100), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("file_extension", sa.String(20)),
        sa.Column("version", sa.Integer(), default=1),
        sa.Column("tags", sa.String(500)),
        sa.Column("created_by", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("read", sa.Boolean(), default=False),
        sa.Column("action_url", sa.String(1000)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "workflows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("campaign_type", sa.String(50)),
        sa.Column("description", sa.String(500)),
        sa.Column("steps", sa.JSON(), default=list),
        sa.Column("status", sa.String(20), default="draft"),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workflow_id", sa.Integer(), sa.ForeignKey("workflows.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("condition", sa.JSON(), default=dict),
        sa.Column("action", sa.JSON(), default=dict),
        sa.Column("delay_seconds", sa.Integer(), default=0),
        sa.Column("max_retries", sa.Integer(), default=0),
        sa.Column("priority", sa.Integer(), default=100),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_type", sa.String(100), nullable=False, index=True),
        sa.Column("entity_type", sa.String(100)),
        sa.Column("entity_id", sa.Integer()),
        sa.Column("data", sa.JSON(), default=dict),
        sa.Column("timestamp", sa.DateTime(timezone=True), index=True),
        sa.Column("processed", sa.Boolean(), default=False, index=True),
    )
    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("template_id", sa.Integer(), sa.ForeignKey("campaign_templates.id", name="fk_campaign_template"), nullable=True),
        sa.Column("workflow_id", sa.Integer(), sa.ForeignKey("workflows.id"), nullable=True),
        sa.Column("settings", sa.JSON(), default={}),
        sa.Column("results", sa.JSON(), default={}),
    )
    op.create_table(
        "campaign_templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id", name="fk_template_campaign"), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("settings", sa.JSON(), default={}),
        sa.Column("audio_ids", sa.JSON(), default=list),
        sa.Column("template_ids", sa.JSON(), default=list),
        sa.Column("caller_profile_id", sa.Integer()),
        sa.Column("provider_ids", sa.JSON(), default=list),
        sa.Column("workflow_id", sa.Integer(), sa.ForeignKey("workflows.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "campaign_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("run_number", sa.Integer(), default=1),
        sa.Column("status", sa.String(20), default="queued"),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("total_contacts", sa.Integer(), default=0),
        sa.Column("total_calls", sa.Integer(), default=0),
        sa.Column("total_messages", sa.Integer(), default=0),
        sa.Column("total_emails", sa.Integer(), default=0),
        sa.Column("success_count", sa.Integer(), default=0),
        sa.Column("failed_count", sa.Integer(), default=0),
        sa.Column("conversion_count", sa.Integer(), default=0),
        sa.Column("cost", sa.Float(), default=0.0),
        sa.Column("duration", sa.Integer(), default=0),
        sa.Column("settings_snapshot", sa.JSON(), default={}),
    )
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("type", sa.String(100), nullable=False),
        sa.Column("subtype", sa.String(100)),
        sa.Column("file_id", sa.Integer(), sa.ForeignKey("stored_files.id")),
        sa.Column("tags", sa.String(500)),
        sa.Column("extra_data", sa.Text()),
        sa.Column("version", sa.Integer(), default=1),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "system_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("value", sa.Text()),
        sa.Column("description", sa.String(500)),
        sa.Column("category", sa.String(50), default="general"),
        sa.Column("is_secret", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "environment_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("environment", sa.String(20), nullable=False),
        sa.Column("app_config", sa.JSON(), default={}),
        sa.Column("feature_flags", sa.JSON(), default={}),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )


def downgrade():
    op.drop_table("environment_configs")
    op.drop_table("system_configs")
    op.drop_table("assets")
    op.drop_table("campaign_runs")
    op.drop_table("campaign_templates")
    op.drop_table("campaigns")
    op.drop_table("events")
    op.drop_table("rules")
    op.drop_table("workflows")
    op.drop_table("notifications")
    op.drop_table("stored_files")
    op.drop_table("users")
