"""WhatsApp Business Cloud API delivery backend.

Delivers campaign messages through the Meta Graph WhatsApp Cloud API
``POST /{phone_number_id}/messages``. Credentials come from a connected
``Provider`` of kind ``whatsapp`` (config: ``token``, ``phone_number_id``).
"""

import requests

from app.modules.dialer.backends.messaging import MessagingBackend


class WhatsAppBackend(MessagingBackend):
    channel = "whatsapp"
    API_BASE = "https://graph.facebook.com/v20.0"

    def __init__(self, config=None, **kwargs):
        super().__init__(config, **kwargs)
        self.token = self.config.get("token") or ""
        self.phone_number_id = self.config.get("phone_number_id") or ""

    def _check(self):
        """Probe the WhatsApp Cloud API (GET messages on the phone id)."""
        if not (self.token and self.phone_number_id):
            return False
        resp = requests.get(
            f"{self.API_BASE}/{self.phone_number_id}/messages",
            params={"limit": 1},
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=15,
        )
        return resp.status_code == 200

    def _api_send(self, body, destination, message=None):
        """Send a WhatsApp text message to ``destination`` (E.164 phone)."""
        if not (self.token and self.phone_number_id):
            raise RuntimeError(
                "WhatsApp token/phone_number_id not configured in campaign"
            )

        payload = {
            "messaging_product": "whatsapp",
            "to": destination,
            "type": "text",
            "text": {"body": body},
        }
        resp = requests.post(
            f"{self.API_BASE}/{self.phone_number_id}/messages",
            json=payload,
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=15,
        )
        data = resp.json()
        if resp.status_code in (200, 201):
            message_id = (
                data.get("messages", [{}])[0].get("id")
                if data.get("messages")
                else None
            )
            return True, message_id, None
        error = data.get("error", {}).get("message") or f"HTTP {resp.status_code}"
        return False, None, error
