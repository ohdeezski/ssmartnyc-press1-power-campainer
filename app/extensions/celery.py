from celery import Celery

# Module-level instance shared by web, worker, and beat.
# `include` lets the worker autodiscover tasks without circular imports.
celery = Celery(
    "street_smart_campaign_center",
    include=["app.modules.taskqueue.tasks", "app.modules.dialer.tasks"],
)
