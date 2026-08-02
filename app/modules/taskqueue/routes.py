from flask import current_app, jsonify
from flask_login import login_required

from app.modules.taskqueue import taskqueue_bp


@taskqueue_bp.route("/status/<task_id>")
@login_required
def task_status(task_id):
    from app.modules.taskqueue.celery_app import create_celery_app

    celery = create_celery_app(current_app)
    result = celery.AsyncResult(task_id)
    return jsonify(
        {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
        }
    )
