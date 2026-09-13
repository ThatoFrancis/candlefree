"""Unit tests for ConflictService using mock providers."""

from datetime import datetime, timedelta

from candlefree.providers.mocks import MockCalendarService, MockLoadSheddingProvider
from candlefree.services.conflict_service import ConflictService

AREA = "demo-area"


def make_service() -> ConflictService:
    return ConflictService(MockLoadSheddingProvider(), MockCalendarService())


def test_schedule_has_stage_and_windows():
    schedule = make_service().get_schedule(AREA)
    assert schedule.current_stage == 4
    assert len(schedule.windows) == 3


def test_finds_client_demo_conflict():
    conflicts = make_service().find_conflicts(AREA)
    titles = [c.meeting.title for c in conflicts]
    assert "Client demo (Zoom)" in titles
    assert "Standup" not in titles


def test_safe_slot_avoids_all_outages():
    service = make_service()
    conflict = next(c for c in service.find_conflicts(AREA) if c.meeting.id == "m2")
    start, end = service.suggest_safe_slot(AREA, conflict.meeting)
    schedule = service.get_schedule(AREA)
    assert all(not w.overlaps(start, end) for w in schedule.windows)
    assert end - start == conflict.meeting.end - conflict.meeting.start


def test_reschedule_updates_calendar():
    calendar = MockCalendarService()
    new_start = datetime.now().replace(hour=16, minute=45, second=0, microsecond=0)
    updated = calendar.reschedule("m2", new_start, new_start + timedelta(hours=1))
    assert updated.start == new_start
    fetched = calendar.get_meetings(new_start - timedelta(minutes=1), new_start + timedelta(hours=2))
    assert any(m.id == "m2" and m.start == new_start for m in fetched)
