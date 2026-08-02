"""Provider service — connect, test, health, failover."""

from app.extensions import db
from app.modules.providers.connectors.asterisk import AsteriskConnector
from app.modules.providers.connectors.twilio import TwilioConnector
from app.modules.providers.connectors.sip import SIPConnector
from app.modules.providers.models import Provider  # noqa: F401 (re-export)


CONNECTOR_MAP = {
    "asterisk": AsteriskConnector,
    "twilio": TwilioConnector,
    "sip": SIPConnector,
}


class ProviderService:
    """Service for managing provider connections."""

    @staticmethod
    def connect(provider_id):
        """Connect to a provider."""
        provider = Provider.query.get(provider_id)
        if not provider:
            return {"error": "Provider not found"}

        connector = CONNECTOR_MAP.get(provider.kind)
        if not connector:
            return {"error": f"Unknown provider kind: {provider.kind}"}

        conn = connector(provider.config or {})
        result = conn.connect()

        provider.status = "connected" if result else "disconnected"
        db.session.commit()

        return {"status": provider.status, "result": result}

    @staticmethod
    def test(provider_id):
        """Test a provider connection."""
        provider = Provider.query.get(provider_id)
        if not provider:
            return {"error": "Provider not found"}

        connector = CONNECTOR_MAP.get(provider.kind)
        if not connector:
            return {"error": f"Unknown provider kind: {provider.kind}"}

        conn = connector(provider.config or {})
        result = conn.test()

        return result

    @staticmethod
    def health(provider_id):
        """Check provider health."""
        provider = Provider.query.get(provider_id)
        if not provider:
            return {"error": "Provider not found"}

        connector = CONNECTOR_MAP.get(provider.kind)
        if not connector:
            return {"error": f"Unknown provider kind: {provider.kind}"}

        conn = connector(provider.config or {})
        return conn.health()

    @staticmethod
    def reconnect(provider_id):
        """Reconnect a provider."""
        provider = Provider.query.get(provider_id)
        if not provider:
            return {"error": "Provider not found"}

        connector = CONNECTOR_MAP.get(provider.kind)
        if not connector:
            return {"error": f"Unknown provider kind: {provider.kind}"}

        conn = connector(provider.config or {})
        result = conn.reconnect()

        provider.status = "connected" if result else "disconnected"
        db.session.commit()

        return {"status": provider.status, "result": result}

    @staticmethod
    def failover(campaign_run_id):
        """Failover to the next available provider."""
        from app.modules.dialer.models import Provider as DialerProvider

        # Find the next connected provider with higher priority
        current = DialerProvider.query.filter_by(status="connected").order_by(
            DialerProvider.priority.asc()
        ).first()

        if current:
            return {"provider_id": current.id, "kind": current.kind}

        return {"error": "No connected providers available"}
