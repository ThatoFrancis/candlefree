"""Abstraction over the user's calendar (Dependency Inversion)."""

from abc import ABC, abstractmethod
from datetime import datetime

from candlefree.domain.models import Meeting


class CalendarService(ABC):
    """Any calendar backend (Google, Outlook, ICS file, mock...)."""

    @abstractmethod
    def get_meetings(self, start: datetime, end: datetime) -> list[Meeting]:
        """Return meetings within a time range."""

    @abstractmethod
    def reschedule(self, meeting_id: str, new_start: datetime, new_end: datetime) -> Meeting:
        """Move a meeting to a new slot and return the updated meeting."""
