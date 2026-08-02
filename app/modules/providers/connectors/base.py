from abc import ABC, abstractmethod


class AbstractProvider(ABC):
    """Abstract base for all provider connectors.

    Every provider connector supports the same operations:
    connect, test, reconnect, set_priority, health, failover,
    enable/disable, edit, delete, view_logs.
    """

    @abstractmethod
    def connect(self, config):
        """Establish a connection to the provider."""

    @abstractmethod
    def test(self):
        """Verify the connection works."""

    @abstractmethod
    def reconnect(self):
        """Re-establish connection after disconnection."""

    @abstractmethod
    def health(self):
        """Return dict with status, latency_ms, uptime."""

    @abstractmethod
    def enable(self):
        """Enable the provider."""

    @abstractmethod
    def disable(self):
        """Disable the provider."""

    @abstractmethod
    def to_dict(self):
        """Return serializable dict representation."""
