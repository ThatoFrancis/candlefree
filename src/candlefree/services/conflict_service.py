"""Business logic: detect conflicts and propose safe slots (Single Responsibility)."""

from datetime import datetime, timedelta

from candlefree.domain.models import AreaSchedule, Conflict, Meeting
from candlefree.interfaces.calendar_service import CalendarService
from candlefree.interfaces.schedule_provider import LoadSheddingProvider


class ConflictService:
    """Finds meetings that collide with outages and suggests power-safe slots."""

    def __init__(self, provider: LoadSheddingProvider, calendar: CalendarService) -> None:
        self._provider = provider
        self._calendar = calendar

    def get_schedule(self, area_id: str) -> AreaSchedule:
        return self._provider.get_schedule(area_id)

    def find_conflicts(self, area_id: str, horizon_hours: int = 24) -> list[Conflict]:
        now = datetime.now()
        end = now + timedelta(hours=horizon_hours)
        schedule = self._provider.get_schedule(area_id)
        meetings = self._calendar.get_meetings(now, end)
        return [
            Conflict(meeting=meeting, outage=window)
            for meeting in meetings
            if meeting.is_online
            for window in schedule.windows
            if window.overlaps(meeting.start, meeting.end)
        ]

    def suggest_safe_slot(self, area_id: str, meeting: Meeting, buffer_minutes: int = 15) -> tuple[datetime, datetime]:
        """Earliest slot after the conflicting outage that avoids all outages."""
        duration = meeting.end - meeting.start
        buffer = timedelta(minutes=buffer_minutes)
        schedule = self._provider.get_schedule(area_id)
        candidate = meeting.start
        for window in sorted(schedule.windows, key=lambda w: w.start):
            if window.overlaps(candidate, candidate + duration):
                candidate = window.end + buffer
        return candidate, candidate + duration
