from abc import ABC, abstractmethod


class DialerBackend(ABC):
    """Abstract base for dialer backends (simulation, asterisk, etc.)."""

    @abstractmethod
    def health(self):
        """Return dict with status, latency_ms, uptime."""

    @abstractmethod
    def launch(self, campaign_run, contacts):
        """Start dialing a campaign run. Returns initial state."""

    @abstractmethod
    def tick(self, campaign_run):
        """Advance the campaign by one tick. Returns updated state."""

    @abstractmethod
    def pause(self, campaign_run):
        """Pause the campaign run."""

    @abstractmethod
    def stop(self, campaign_run):
        """Stop the campaign run."""

    @abstractmethod
    def status(self, campaign_run):
        """Return current status dict for the campaign run."""
