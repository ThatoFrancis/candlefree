"""Abstraction over notification channels (Dependency Inversion)."""

from abc import ABC, abstractmethod

from candlefree.domain.models import Alert


class Notifier(ABC):
    """Any alert channel (console, WhatsApp, SNS, email...)."""

    @abstractmethod
    def send(self, alert: Alert) -> None:
        """Deliver an alert to the user."""
