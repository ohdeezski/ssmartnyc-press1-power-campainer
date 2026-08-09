"""Telegram Bot API delivery backend.

Delivers campaign messages to Telegram chat ids via the Bot API
``sendMessage`` endpoint. Credentials come from a connected ``Provider``
of kind ``telegram`` (config: ``token``).
"""

import requests

from app.modules.dialer.backends.messaging import MessagingBackend


class TelegramBackend(MessagingBackend):
    channel = "telegram"
    API_BASE = "https://api.telegram.org"

    def __init__(self, config=None, **kwargs):
        super().__init__(config, **kwargs)
        self.token = self.config.get("token") or ""
        self.parse_mode = self.config.get("parse_mode", "HTML")

    def _check(self):
        """Probe the Bot API getMe to confirm the token is valid."""
        if not self.token:
            return False
        resp = requests.get(
            f"{self.API_BASE}/bot{self.token}/getMe",
            timeout=15,
        )
        return resp.status_code == 200 and resp.json().get("ok", False)

    def _api_send(self, body, destination, message=None):
        """Send a Telegram message to ``destination`` (chat id)."""
        if not self.token:
            return False, None, "Telegram bot token not configured in campaign"

        payload = {
            "chat_id": destination,
            "text": body,
        }
        if self.parse_mode:
            payload["parse_mode"] = self.parse_mode
        resp = requests.post(
            f"{self.API_BASE}/bot{self.token}/sendMessage",
            json=payload,
            timeout=15,
        )
        data = resp.json()
        if resp.status_code == 200 and data.get("ok"):
            message_id = data.get("result", {}).get("message_id")
            return True, message_id, None
        return False, None, data.get("description") or f"HTTP {resp.status_code}"
