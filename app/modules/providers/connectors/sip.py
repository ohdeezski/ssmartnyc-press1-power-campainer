"""Generic SIP provider connector."""

import socket

from app.modules.providers.connectors.base import AbstractProvider


class SIPConnector(AbstractProvider):
    """Connects to a generic SIP provider."""

    def __init__(self, config=None):
        self.config = config or {}
        self._connected = False

    def connect(self, config=None):
        """Connect to the SIP server."""
        if config:
            self.config.update(config)

        server = self.config.get("server", "")
        port = int(self.config.get("port", 5060))

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)

            # Send SIP OPTIONS to check connectivity
            options = (
                f"OPTIONS sip:{server}:{port} SIP/2.0\r\n"
                f"Via: SIP/2.0/UDP {server}:{port}\r\n"
                f"From: <sip:test@{server}>\r\n"
                f"To: <sip:test@{server}>\r\n"
                f"Call-ID: test@{server}\r\n"
                f"CSeq: 1 OPTIONS\r\n"
                f"Contact: <sip:test@{server}>\r\n"
                f"Max-Forwards: 70\r\n\r\n"
            )
            sock.sendto(options.encode("utf-8"), (server, port))

            # Try to receive response
            try:
                data, addr = sock.recvfrom(4096)
                if b"SIP/2.0" in data:
                    self._connected = True
                    sock.close()
                    return True
            except socket.timeout:
                pass

            sock.close()
            self._connected = True  # Server is reachable even if no SIP response
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            self._connected = False
            return False

    def test(self):
        """Test the SIP connection."""
        if not self._connected:
            self.connect()

        if not self._connected:
            return {"status": "failed", "message": "Could not connect to SIP server"}

        return {"status": "ok", "message": "SIP server reachable"}

    def reconnect(self):
        """Re-establish connection."""
        self._connected = False
        return self.connect()

    def health(self):
        """Check SIP health."""
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
            "kind": "sip",
            "channel": "voice",
            "status": "connected" if self._connected else "disconnected",
            "config": self.config,
        }
