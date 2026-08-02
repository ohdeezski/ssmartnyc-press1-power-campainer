"""Asterisk provider connector."""

import os
import socket

from app.modules.providers.connectors.base import AbstractProvider


class AsteriskConnector(AbstractProvider):
    """Connects to an Asterisk server via AMI and/or call files."""

    def __init__(self, config=None):
        self.config = config or {}
        self._connected = False
        self._socket = None

    def connect(self, config=None):
        """Connect to the Asterisk server."""
        if config:
            self.config.update(config)

        host = self.config.get("host", "127.0.0.1")
        port = int(self.config.get("port", 5038))
        username = self.config.get("username", "admin")
        secret = self.config.get("secret", "admin")

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(10)
            self._socket.connect((host, port))

            # Read greeting
            greeting = self._socket.recv(4096).decode("utf-8")
            if "Asterisk Call Manager" not in greeting:
                self._connected = False
                return False

            # Login
            login = f"Action: Login\r\nUsername: {username}\r\nSecret: {secret}\r\n\r\n"
            self._socket.sendall(login.encode("utf-8"))
            response = self._socket.recv(4096).decode("utf-8")

            if "Response: Success" in response:
                self._connected = True
                return True
            return False
        except (socket.timeout, ConnectionRefusedError, OSError):
            self._connected = False
            return False

    def test(self):
        """Test the Asterisk connection."""
        if not self._connected:
            self.connect()

        if not self._connected:
            return {"status": "failed", "message": "Could not connect to Asterisk"}

        # Check if call file directory exists
        call_file_dir = self.config.get("call_file_dir", "/var/spool/asterisk/outgoing")
        if os.path.isdir(call_file_dir):
            return {
                "status": "ok",
                "message": "Asterisk connected, call file dir accessible",
            }

        return {"status": "ok", "message": "Asterisk AMI connected"}

    def reconnect(self):
        """Re-establish connection."""
        self._connected = False
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
        return self.connect()

    def health(self):
        """Check Asterisk health."""
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
        if self._socket:
            try:
                self._socket.sendall(b"Action: Logoff\r\n\r\n")
            except Exception:
                pass
            try:
                self._socket.close()
            except Exception:
                pass

    def to_dict(self):
        return {
            "kind": "asterisk",
            "channel": "voice",
            "status": "connected" if self._connected else "disconnected",
            "config": self.config,
        }
