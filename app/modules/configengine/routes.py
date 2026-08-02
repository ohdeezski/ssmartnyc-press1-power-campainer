from flask import jsonify, request
from flask_login import current_user, login_required

from app.modules.configengine import configengine_bp
from app.modules.configengine.services import config_service


def _can_edit_configs():
    """Only admins and managers may change system/configuration state."""
    return current_user.role in ("admin", "manager")


def _redact_secrets(value, depth=0):
    """Mask string values under secret-looking keys (recursively, 2 levels)."""
    secret_markers = ("secret", "password", "token", "api", "key", "credential")
    if depth > 1:
        return value
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if isinstance(v, str) and any(m in k.lower() for m in secret_markers):
                out[k] = "***REDACTED***"
            elif isinstance(v, (dict, list)):
                out[k] = _redact_secrets(v, depth + 1)
            else:
                out[k] = v
        return out
    if isinstance(value, list):
        return [_redact_secrets(v, depth + 1) for v in value]
    return value


@configengine_bp.route("/system", methods=["GET"])
@login_required
def get_system_configs():
    """Get all system configuration values"""
    try:
        category = request.args.get("category")
        configs = config_service.get_all_system_configs(category)

        # Hide secret values
        for config in configs:
            if config.get("is_secret"):
                config["value"] = "***REDACTED***"

        return jsonify({"success": True, "configs": configs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@configengine_bp.route("/system", methods=["POST"])
@login_required
def set_system_config():
    """Set or update a system configuration value"""
    if not _can_edit_configs():
        return jsonify({"success": False, "error": "Forbidden"}), 403

    try:
        data = request.get_json()
        if not data or "key" not in data:
            return jsonify({"success": False, "error": "Key is required"}), 400

        key = data["key"]
        value = data.get("value")
        description = data.get("description", "")
        category = data.get("category", "general")
        is_secret = data.get("is_secret", False)

        config = config_service.set_system_config(
            key=key,
            value=value,
            description=description,
            category=category,
            is_secret=is_secret,
        )

        return jsonify({"success": True, "config": config.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@configengine_bp.route("/environment", methods=["GET"])
@login_required
def get_environment_configs():
    """Get environment configuration"""
    try:
        environment = request.args.get("environment")
        configs = config_service.get_environment_config(environment)

        # Mask secret-looking values before they leave the API.
        if isinstance(configs, dict) and "app_config" in configs:
            configs["app_config"] = _redact_secrets(configs["app_config"])
        elif isinstance(configs, dict):
            configs = _redact_secrets(configs)

        return jsonify({"success": True, "configs": configs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@configengine_bp.route("/environment", methods=["POST"])
@login_required
def set_environment_config():
    """Set environment configuration"""
    if not _can_edit_configs():
        return jsonify({"success": False, "error": "Forbidden"}), 403

    try:
        data = request.get_json()
        if not data or "environment" not in data or "app_config" not in data:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Environment and app_config are required",
                    }
                ),
                400,
            )

        environment = data["environment"]
        app_config = data["app_config"]
        feature_flags = data.get("feature_flags", {})

        config = config_service.set_environment_config(
            environment=environment, app_config=app_config, feature_flags=feature_flags
        )

        return jsonify({"success": True, "config": config.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@configengine_bp.route("/feature-flags", methods=["GET"])
@login_required
def get_feature_flags():
    """Get all feature flags"""
    try:
        configs = config_service.get_all_system_configs("feature_flags")

        # Filter to only show feature flags (non-secret)
        feature_flags = {}
        for config in configs:
            if not config.get("is_secret"):
                key = config["key"].replace("feature_", "")
                feature_flags[key] = config["value"].lower() == "true"

        return jsonify({"success": True, "feature_flags": feature_flags})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@configengine_bp.route("/feature-flags", methods=["POST"])
@login_required
def set_feature_flag():
    """Set a feature flag"""
    if not _can_edit_configs():
        return jsonify({"success": False, "error": "Forbidden"}), 403

    try:
        data = request.get_json()
        if not data or "key" not in data or "enabled" not in data:
            return (
                jsonify({"success": False, "error": "Key and enabled are required"}),
                400,
            )

        key = data["key"]
        enabled = data["enabled"]

        config_service.set_feature_flag(key, enabled)

        return jsonify(
            {"success": True, "message": f"Feature flag '{key}' set to {enabled}"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
