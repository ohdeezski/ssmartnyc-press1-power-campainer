from app.extensions import db
from app.modules.notifications.models import Notification


def create_notification(user_id, notification_type, title, message, action_url=None):
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        action_url=action_url,
    )
    db.session.add(notification)
    db.session.commit()
    return notification


def send_toast(user_id, message):
    return create_notification(user_id, "info", "Notification", message)


def send_warning(user_id, message):
    return create_notification(user_id, "warning", "Warning", message)


def send_error(user_id, message):
    return create_notification(user_id, "error", "Error", message)


def send_success(user_id, message):
    return create_notification(user_id, "success", "Success", message)
