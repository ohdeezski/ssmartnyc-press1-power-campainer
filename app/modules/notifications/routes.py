from flask import jsonify, request
from flask_login import current_user, login_required

from app.extensions import db
from app.modules.notifications import notifications_bp
from app.modules.notifications.models import Notification
from app.modules.notifications.services import (
    create_notification,
    send_error,
    send_toast,
    send_warning,
)


@notifications_bp.route("/", methods=["GET"])
@login_required
def list_notifications():
    notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return jsonify([n.to_dict() for n in notifications])


@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    # Only the recipient (or a user with view_all) may mark a notification read.
    if notification.user_id != current_user.id and not current_user.has_permission(
        "view_all"
    ):
        return jsonify({"error": "Unauthorized"}), 403
    notification.read = True
    db.session.commit()
    return jsonify({"status": "ok"})


@notifications_bp.route("/read-all", methods=["POST"])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, read=False).update(
        {"read": True}
    )
    db.session.commit()
    return jsonify({"status": "ok"})


# Toast-style notification endpoints
@notifications_bp.route("/toast/success", methods=["POST"])
@login_required
def send_toast_endpoint():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    notification = send_toast(current_user.id, data["message"])
    return jsonify(notification.to_dict()), 201


@notifications_bp.route("/toast/warning", methods=["POST"])
@login_required
def send_warning_endpoint():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    notification = send_warning(current_user.id, data["message"])
    return jsonify(notification.to_dict()), 201


@notifications_bp.route("/toast/error", methods=["POST"])
@login_required
def send_error_endpoint():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    notification = send_error(current_user.id, data["message"])
    return jsonify(notification.to_dict()), 201


@notifications_bp.route("/toast/info", methods=["POST"])
@login_required
def send_info_endpoint():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    notification = send_toast(current_user.id, data["message"])
    return jsonify(notification.to_dict()), 201


# Admin notification endpoints
@notifications_bp.route("/admin", methods=["POST"])
@login_required
def create_admin_notification():
    from app.modules.auth.models import User

    # Only users who can manage users may send admin notifications.
    if not current_user.has_permission("manage_users"):
        return jsonify({"error": "Admin privileges required"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Data is required"}), 400

    if not data.get("user_id") or not data.get("message") or not data.get("title"):
        return jsonify({"error": "user_id, title, and message are required"}), 400

    # Check if current user has permission to send admin notifications
    user = User.query.get(data["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    notification_type = data.get("type", "info")
    title = data["title"]
    message = data["message"]
    action_url = data.get("action_url")

    notification = create_notification(
        user.id, notification_type, title, message, action_url
    )

    return jsonify(notification.to_dict()), 201
