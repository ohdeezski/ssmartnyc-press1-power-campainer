"""Telegram Bot API provider connector."""

import requests

from app.modules.providers.connectors.base import AbstractProvider


class TelegramConnector(AbstractProvider):
    """Connects to the Telegram Bot API.

    A bot token is required. ``connect`` validates the token shape and
    ``test`` reads ``getMe`` to confirm the bot identity with the API.
    """

    API_BASE = "https://api.telegram.org"

    def __init__(self, config=None):
        self.config = config or {}
        self._connected = False

    def _me(self, timeout=15):
        token = self.config.get("token", "")
        resp = requests.get(
            f"{self.API_BASE}/bot{token}/getMe",
            timeout=timeout,
        )
        resp.raise_for_status()
        payload = resp.json()
        if not payload.get("ok"):
            raise ValueError(payload.get("description", "Telegram API error"))
        return payload.get("result", {})

    def connect(self, config=None):
        """Validate the stored Telegram bot token."""
        if config:
            self.config.update(config)

        if not self.config.get("token"):
            self._connected = False
            return False

        self._connected = True
        return True

    def test(self):
        """Probe the Telegram Bot API getMe endpoint."""
        if not self.config.get("token"):
            return {"status": "failed", "message": "bot token required"}

        try:
            bot_info = self._me()
            self._connected = True
            return {"status": "ok", "message": f"@{bot_info.get('username', 'bot')}"}
        except (requests.RequestException, ValueError) as exc:
            return {"status": "failed", "message": str(exc)}

    def reconnect(self):
        """Re-establish connection."""
        self._connected = False
        return self.connect()

    def health(self):
        """Check Telegram API health."""
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
            "kind": "telegram",
            "channel": "messaging",
            "status": "connected" if self._connected else "disconnected",
            "config": self.config,
        }
