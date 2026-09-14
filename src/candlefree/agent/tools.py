"""Strands tools — thin adapters exposing services to the agent."""

from datetime import datetime, timedelta

from strands import tool

from candlefree.agent.container import get_container
from candlefree.domain.models import Alert, Severity


@tool
def get_loadshedding_schedule() -> str:
    """Get the current load shedding stage and upcoming outage windows for the user's area."""
    c = get_container()
    schedule = c.conflict_service.get_schedule(c.area_id)
    lines = [f"Area: {schedule.area_name} | Current stage: {schedule.current_stage}"]
    lines += [
        f"- Stage {w.stage} outage: {w.start:%a %H:%M} to {w.end:%H:%M}" for w in schedule.windows
    ]
    return "\n".join(lines)


@tool
def find_meeting_conflicts() -> str:
    """Find online meetings in the next 24h that clash with load shedding outages."""
    c = get_container()
    conflicts = c.conflict_service.find_conflicts(c.area_id)
    if not conflicts:
        return "No conflicts. All meetings are power-safe."
    return "\n".join(
        f"CONFLICT: '{x.meeting.title}' (id={x.meeting.id}, {x.meeting.start:%H:%M}-{x.meeting.end:%H:%M}) "
        f"overlaps Stage {x.outage.stage} outage {x.outage.start:%H:%M}-{x.outage.end:%H:%M}"
        for x in conflicts
    )


@tool
def suggest_safe_slot(meeting_id: str) -> str:
    """Suggest the earliest power-safe slot to move a conflicting meeting to.

    Args:
        meeting_id: The id of the conflicting meeting.
    """
    c = get_container()
    meetings = {
        m.id: m
        for m in c.calendar.get_meetings(datetime.now(), datetime.now() + timedelta(hours=48))
    }
    meeting = meetings.get(meeting_id)
    if meeting is None:
        return f"Meeting {meeting_id} not found."
    start, end = c.conflict_service.suggest_safe_slot(c.area_id, meeting)
    return (
        f"Safe slot for '{meeting.title}': {start:%a %d %b %Y %H:%M} to {end:%H:%M}. "
        f"To move it, call reschedule_meeting with EXACTLY new_start_iso='{start:%Y-%m-%dT%H:%M}' "
        f"and new_end_iso='{end:%Y-%m-%dT%H:%M}'."
    )


@tool
def reschedule_meeting(meeting_id: str, new_start_iso: str, new_end_iso: str) -> str:
    """Reschedule a meeting to a new time.

    Args:
        meeting_id: The id of the meeting to move.
        new_start_iso: New start time in ISO format (YYYY-MM-DDTHH:MM).
        new_end_iso: New end time in ISO format (YYYY-MM-DDTHH:MM).
    """
    c = get_container()
    new_start = datetime.fromisoformat(new_start_iso)
    new_end = datetime.fromisoformat(new_end_iso)
    if new_start < datetime.now():
        return (
            f"ERROR: {new_start_iso} is in the past (now is {datetime.now():%Y-%m-%dT%H:%M}). "
            "Use the exact ISO times returned by suggest_safe_slot."
        )
    updated = c.calendar.reschedule(meeting_id, new_start, new_end)
    return f"Rescheduled '{updated.title}' to {updated.start:%a %d %b %H:%M}-{updated.end:%H:%M}."


@tool
def notify_user(severity: str, title: str, body: str) -> str:
    """Send an alert to the user. Use ONLY when a human decision or awareness is truly needed.

    Args:
        severity: One of 'info', 'warning', 'decision_required'.
        title: Short alert headline.
        body: Alert details, including any recommendation.
    """
    c = get_container()
    c.notifier.send(Alert(severity=Severity(severity), title=title, body=body))
    return "Alert delivered."

