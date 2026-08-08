"""SMTP email provider connector."""

import smtplib

from app.modules.providers.connectors.base import AbstractProvider


class SMTPConnector(AbstractProvider):
    """Connects to an SMTP relay for transactional email delivery."""

    def __init__(self, config=None):
        self.config = config or {}
        self._connected = False

    def _connect_smtp(self):
        """Open a live SMTP connection and return the server object."""
        host = self.config.get("host", "")
        port = int(self.config.get("port", 587))
        user = self.config.get("user", "")
        password = self.config.get("password", "")

        server = smtplib.SMTP(host, port, timeout=15)
        try:
            if self.config.get("use_tls", True):
                server.starttls()
            if user and password:
                server.login(user, password)
            return server
        except Exception:
            server.quit()
            raise

    def connect(self, config=None):
        """Connect to the SMTP server."""
        if config:
            self.config.update(config)

        try:
            server = self._connect_smtp()
            server.quit()
            self._connected = True
            return True
        except (smtplib.SMTPException, OSError):
            self._connected = False
            return False

    def test(self):
        """Test the SMTP connection."""
        if not self._connected:
            self.connect()

        if not self._connected:
            return {"status": "failed", "message": "Could not connect to SMTP server"}

        return {"status": "ok", "message": "SMTP server reachable"}

    def reconnect(self):
        """Re-establish connection."""
        self._connected = False
        return self.connect()

    def health(self):
        """Check SMTP health."""
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
            "kind": "smtp",
            "channel": "email",
            "status": "connected" if self._connected else "disconnected",
            "config": self.config,
        }
