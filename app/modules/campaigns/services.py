from app.extensions import db
from app.modules.campaigns.models import Campaign, CampaignRun, CampaignTemplate


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
    def launch_campaign(campaign_id):
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return None
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
