"""In-memory mock providers for demos and tests (Liskov-substitutable)."""

from datetime import datetime, timedelta

from candlefree.domain.models import Alert, AreaOption, AreaSchedule, Meeting, OutageWindow
from candlefree.interfaces.calendar_service import CalendarService
from candlefree.interfaces.notifier import Notifier
from candlefree.interfaces.schedule_provider import LoadSheddingProvider


def _today_at(hour: int, minute: int = 0) -> datetime:
    return datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)


def _base() -> datetime:
    """Anchor for relative demo data — the current quarter hour."""
    now = datetime.now().replace(second=0, microsecond=0)
    return now - timedelta(minutes=now.minute % 15)


class MockLoadSheddingProvider(LoadSheddingProvider):
    """Deterministic Stage 4 demo: an outage always starts ~45 min from now."""

    def get_schedule(self, area_id: str) -> AreaSchedule:
        base = _base()
        return AreaSchedule(
            area_id=area_id,
            area_name=f"{area_id} (demo)",
            current_stage=4,
            windows=[
                OutageWindow(
                    stage=4,
                    start=base + timedelta(minutes=45),
                    end=base + timedelta(hours=3, minutes=15),
                ),
                OutageWindow(
                    stage=4,
                    start=base + timedelta(hours=7),
                    end=base + timedelta(hours=9, minutes=30),
                ),
                OutageWindow(
                    stage=4,
                    start=base + timedelta(hours=16),
                    end=base + timedelta(hours=18, minutes=30),
                ),
            ],
        )

    def search_areas(self, text: str) -> list[AreaOption]:
        # Demo mode has no area registry — the UI falls back to OpenStreetMap suggestions.
        return []


class MockCalendarService(CalendarService):
    """A demo workday: one meeting collides with the upcoming outage."""

    def __init__(self) -> None:
        base = _base()
        self._meetings: dict[str, Meeting] = {
            m.id: m
            for m in [
                Meeting(
                    id="m1",
                    title="Standup",
                    start=base - timedelta(hours=2),
                    end=base - timedelta(hours=1, minutes=30),
                ),
                Meeting(
                    id="m2",
                    title="Client demo (Zoom)",
                    start=base + timedelta(hours=1, minutes=15),
                    end=base + timedelta(hours=2, minutes=15),
                ),
                Meeting(
                    id="m3",
                    title="1:1 with manager",
                    start=base + timedelta(hours=5),
                    end=base + timedelta(hours=5, minutes=30),
                ),
            ]
        }

    def get_meetings(self, start: datetime, end: datetime) -> list[Meeting]:
        return [m for m in self._meetings.values() if m.start < end and start < m.end]

    def reschedule(self, meeting_id: str, new_start: datetime, new_end: datetime) -> Meeting:
        meeting = self._meetings[meeting_id]
        updated = meeting.model_copy(update={"start": new_start, "end": new_end})
        self._meetings[meeting_id] = updated
        return updated


class ConsoleNotifier(Notifier):
    """Prints alerts and records them for the API/demo UI."""

    def __init__(self) -> None:
        self.sent: list[Alert] = []

    def send(self, alert: Alert) -> None:
        self.sent.append(alert)
        message = f"[{alert.severity.value.upper()}] {alert.title}\n{alert.body}\n"
        try:
            print(message)
        except UnicodeEncodeError:  # Windows consoles without UTF-8 (cp1252)
            print(message.encode("ascii", errors="replace").decode("ascii"))
