"""Celery tasks for the campaign center.

Phase 0 ships a single `ping` task so the worker (and eager task path in tests)
is exercised end to end. Real campaign/audio/report tasks land in Phase 2.
"""

from app.extensions.celery import celery


@celery.task(name="app.ping")
def ping(payload=None):
    return {"pong": True, "payload": payload}
