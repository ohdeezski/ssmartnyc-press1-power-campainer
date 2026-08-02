"""Celery entry point for `celery -A app.modules.taskqueue.celery_app`.

The module exposes a module-level `celery` (the shared instance from
app.extensions.celery) so both the CLI worker and the Flask app converge on
one configuration. `create_celery_app` remains for callers that want the
Flask config applied on demand (e.g. the task-status route).
"""

from app.extensions.celery import celery


def create_celery_app(app=None):
    if app is not None:
        celery.conf.update(
            broker_url=app.config.get("CELERY_BROKER_URL"),
            result_backend=app.config.get("CELERY_RESULT_BACKEND"),
            task_always_eager=app.config.get("CELERY_TASK_ALWAYS_EAGER", False),
        )
    return celery


__all__ = ["celery", "create_celery_app"]
