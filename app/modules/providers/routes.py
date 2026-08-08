from flask import jsonify, request
from flask_login import login_required

from app.extensions import db
from app.modules.providers import providers_bp
from app.modules.providers.models import Provider
from app.modules.providers.services import ProviderService


@providers_bp.route("/", methods=["GET"])
@login_required
def list_providers():
    """List all providers."""
    providers = Provider.query.all()
    return jsonify([p.to_dict() for p in providers])


@providers_bp.route("/", methods=["POST"])
@login_required
def create_provider():
    """Create a new provider."""
    data = request.get_json() or {}
    kind = data.get("kind", "").strip()
    if kind not in ("asterisk", "twilio", "sip", "whatsapp", "smtp", "telegram"):
        return jsonify({"error": f"Invalid provider kind: {kind}"}), 400
    provider = Provider(
        kind=kind,
        channel=data.get("channel", "voice"),
        status=data.get("status", "disconnected"),
        priority=data.get("priority", 1),
        latency_ms=data.get("latency_ms"),
        config=data.get("config", {}),
    )
    db.session.add(provider)
    db.session.commit()
    return jsonify(provider.to_dict()), 201


@providers_bp.route("/<int:provider_id>", methods=["GET"])
@login_required
def get_provider(provider_id):
    """Get a specific provider."""
    provider = Provider.query.get_or_404(provider_id)
    return jsonify(provider.to_dict())


@providers_bp.route("/<int:provider_id>", methods=["PUT"])
@login_required
def update_provider(provider_id):
    """Update a provider."""
    provider = Provider.query.get_or_404(provider_id)
    data = request.get_json() or {}
    kind = data.get("kind", provider.kind)
    if kind not in ("asterisk", "twilio", "sip", "whatsapp", "smtp", "telegram"):
        return jsonify({"error": f"Invalid provider kind: {kind}"}), 400
    provider.kind = kind
    provider.channel = data.get("channel", provider.channel)
    provider.status = data.get("status", provider.status)
    provider.priority = data.get("priority", provider.priority)
    provider.latency_ms = data.get("latency_ms", provider.latency_ms)
    provider.config = data.get("config", provider.config)
    db.session.commit()
    return jsonify(provider.to_dict())


@providers_bp.route("/<int:provider_id>", methods=["DELETE"])
@login_required
def delete_provider(provider_id):
    """Delete a provider."""
    provider = Provider.query.get_or_404(provider_id)
    db.session.delete(provider)
    db.session.commit()
    return jsonify({"message": "Provider deleted successfully"})


@providers_bp.route("/<int:provider_id>/connect", methods=["POST"])
@login_required
def connect_provider(provider_id):
    """Connect to a provider."""
    result = ProviderService.connect(provider_id)
    return jsonify(result)


@providers_bp.route("/<int:provider_id>/test", methods=["POST"])
@login_required
def test_provider(provider_id):
    """Test a provider connection."""
    result = ProviderService.test(provider_id)
    return jsonify(result)


@providers_bp.route("/<int:provider_id>/health", methods=["GET"])
@login_required
def health_provider(provider_id):
    """Check provider health."""
    result = ProviderService.health(provider_id)
    return jsonify(result)


@providers_bp.route("/<int:provider_id>/reconnect", methods=["POST"])
@login_required
def reconnect_provider(provider_id):
    """Reconnect a provider."""
    result = ProviderService.reconnect(provider_id)
    return jsonify(result)


@providers_bp.route("/failover", methods=["POST"])
@login_required
def provider_failover():
    """Failover to the next available provider."""
    data = request.get_json() or {}
    result = ProviderService.failover(data.get("campaign_run_id"))
    return jsonify(result)
