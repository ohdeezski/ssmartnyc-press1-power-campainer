from flask import Blueprint, request, jsonify

from app.extensions import db
from app.modules.providers.models import Provider
from app.modules.providers.services import ProviderService

providers_bp = Blueprint("providers", __name__, url_prefix="/api/providers")


@providers_bp.route("/", methods=["GET"])
def list_providers():
    """List all providers."""
    providers = Provider.query.all()
    return jsonify([p.to_dict() for p in providers])


@providers_bp.route("/", methods=["POST"])
def create_provider():
    """Create a new provider."""
    data = request.get_json() or {}
    provider = Provider(
        kind=data.get("kind", "").strip(),
        channel=data.get("channel", "").strip(),
        status=data.get("status", "disconnected"),
        priority=data.get("priority", 1),
        latency_ms=data.get("latency_ms"),
        config=data.get("config", {}),
    )
    db.session.add(provider)
    db.session.commit()
    return jsonify(provider.to_dict()), 201


@providers_bp.route("/<int:provider_id>", methods=["GET"])
def get_provider(provider_id):
    """Get a specific provider."""
    provider = Provider.query.get_or_404(provider_id)
    return jsonify(provider.to_dict())


@providers_bp.route("/<int:provider_id>", methods=["PUT"])
def update_provider(provider_id):
    """Update a provider."""
    provider = Provider.query.get_or_404(provider_id)
    data = request.get_json() or {}
    provider.kind = data.get("kind", provider.kind).strip()
    provider.channel = data.get("channel", provider.channel).strip()
    provider.status = data.get("status", provider.status)
    provider.priority = data.get("priority", provider.priority)
    provider.latency_ms = data.get("latency_ms", provider.latency_ms)
    provider.config = data.get("config", provider.config)
    db.session.commit()
    return jsonify(provider.to_dict())


@providers_bp.route("/<int:provider_id>", methods=["DELETE"])
def delete_provider(provider_id):
    """Delete a provider."""
    provider = Provider.query.get_or_404(provider_id)
    db.session.delete(provider)
    db.session.commit()
    return jsonify({"message": "Provider deleted successfully"})


@providers_bp.route("/<int:provider_id>/connect", methods=["POST"])
def connect_provider(provider_id):
    """Connect to a provider."""
    result = ProviderService.connect(provider_id)
    return jsonify(result)


@providers_bp.route("/<int:provider_id>/test", methods=["POST"])
def test_provider(provider_id):
    """Test a provider connection."""
    result = ProviderService.test(provider_id)
    return jsonify(result)


@providers_bp.route("/<int:provider_id>/health", methods=["GET"])
def health_provider(provider_id):
    """Check provider health."""
    result = ProviderService.health(provider_id)
    return jsonify(result)


@providers_bp.route("/<int:provider_id>/reconnect", methods=["POST"])
def reconnect_provider(provider_id):
    """Reconnect a provider."""
    result = ProviderService.reconnect(provider_id)
    return jsonify(result)


@providers_bp.route("/failover", methods=["POST"])
def provider_failover(campaign_run_id=None):
    """Failover to the next available provider."""
    data = request.get_json() or {}
    result = ProviderService.failover(data.get("campaign_run_id"))
    return jsonify(result)