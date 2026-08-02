from celery import shared_task
from app.modules.dialer.services import DialerService


@shared_task(name="dialer.run_campaign")
def run_campaign(campaign_run_id):
    """Celery task to run a campaign through the dialer backend."""
    service = DialerService()
    return service.execute(campaign_run_id)
