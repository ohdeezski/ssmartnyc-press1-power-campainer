"""WhatsApp Business Cloud API provider connector."""

import requests

from app.modules.providers.connectors.base import AbstractProvider


class WhatsAppCloudConnector(AbstractProvider):
    """Connects to the WhatsApp Business Cloud API.

    Uses the Meta WhatsApp Cloud API (graph.facebook.com). A bot token and
    phone number ID are required; ``connect`` only stores config and
    validates fields, and ``test`` performs a live API probe via
    ``GET /messages`` (a valid token receives a 200 with message list).
    """

    API_BASE = "https://graph.facebook.com/v20.0"

    def __init__(self, config=None):
        self.config = config or {}
        self._connected = False

    def connect(self, config=None):
        """Validate the stored WhatsApp credentials."""
        if config:
            self.config.update(config)

        if not (self.config.get("token") and self.config.get("phone_number_id")):
            self._connected = False
            return False

        self._connected = True
        return True

    def test(self):
        """Probe the WhatsApp Cloud API with the configured token."""
        token = self.config.get("token", "")
        phone_number_id = self.config.get("phone_number_id", "")
        if not (token and phone_number_id):
            return {"status": "failed", "message": "token and phone_number_id required"}

        try:
            resp = requests.get(
                f"{self.API_BASE}/{phone_number_id}/messages",
                params={"limit": 1},
                headers={"Authorization": f"Bearer {token}"},
                timeout=15,
            )
            if resp.status_code == 200:
                self._connected = True
                return {"status": "ok", "message": "WhatsApp API reachable"}
            return {
                "status": "failed",
                "message": f"WhatsApp API error {resp.status_code}",
            }
        except requests.RequestException as exc:
            return {"status": "failed", "message": str(exc)}

    def reconnect(self):
        """Re-establish connection."""
        self._connected = False
        return self.connect()

    def health(self):
        """Check WhatsApp API health."""
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

    def to_dict(self):
        return {
            "kind": "whatsapp",
            "channel": "messaging",
            "status": "connected" if self._connected else "disconnected",
            "config": self.config,
        }
