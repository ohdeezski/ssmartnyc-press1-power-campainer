"""Celery wiring: the shared instance must be configurable and run tasks eagerly in tests."""

from app.extensions.celery import celery
from app.modules.taskqueue.tasks import ping


def test_shared_celery_instance_configured(app):
    assert celery.conf.broker_url == app.config["CELERY_BROKER_URL"]
    assert celery.conf.task_always_eager is True  # testing config


def test_ping_task_runs_eagerly(auth_user):
    result = ping.apply(args=["hello"])
    assert result.get() == {"pong": True, "payload": "hello"}


def test_taskqueue_status_route(auth_user):
    resp = auth_user.get("/api/tasks/status/nonexistent-id")
    assert resp.status_code == 200
