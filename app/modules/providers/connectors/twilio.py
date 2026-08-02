"""Twilio provider connector."""

from app.modules.providers.connectors.base import AbstractProvider


class TwilioConnector(AbstractProvider):
    """Connects to Twilio for voice and messaging."""

    def __init__(self, config=None):
        self.config = config or {}
        self._connected = False
        self._client = None

    def _get_client(self):
        """Lazily initialize the Twilio client."""
        if self._client is None:
            from twilio.rest import Client

            self._client = Client(
                self.config.get("account_sid", ""),
                self.config.get("auth_token", ""),
            )
        return self._client

    def connect(self, config=None):
        """Connect to Twilio."""
        if config:
            self.config.update(config)

        try:
            client = self._get_client()
            client.calls.list(limit=1)
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False

    def test(self):
        """Test the Twilio connection."""
        if not self._connected:
            self.connect()

        if not self._connected:
            return {"status": "failed", "message": "Could not connect to Twilio"}

        return {"status": "ok", "message": "Twilio connected"}

    def reconnect(self):
        """Re-establish connection."""
        self._connected = False
        self._client = None
        return self.connect()

    def health(self):
        """Check Twilio health."""
        import time

        start = time.time()
        connected = self._connected or self.connect()
        latency = int((time.time() - start) * 1000)
        return {
            "status": "healthy" if connected else "unhealthy",
            "latency_ms": latency,
            "uptime": 1.0 if connected else 0.0,
        }

    def enable(self):
        """Enable the provider."""
        self._connected = True

    def disable(self):
        """Disable the provider."""
        self._connected = False
        self._client = None

    def to_dict(self):
        return {
            "kind": "twilio",
            "channel": "voice",
            "status": "connected" if self._connected else "disconnected",
            "config": self.config,
        }
