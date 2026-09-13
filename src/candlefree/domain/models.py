"""Domain models — pure data, no I/O (Single Responsibility)."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    DECISION_REQUIRED = "decision_required"


class OutageWindow(BaseModel):
    """A single load shedding slot for an area."""

    stage: int = Field(ge=0, le=8)
    start: datetime
    end: datetime

    def overlaps(self, other_start: datetime, other_end: datetime) -> bool:
        return self.start < other_end and other_start < self.end


class AreaSchedule(BaseModel):
    """Load shedding schedule for one area."""

    area_id: str
    area_name: str
    current_stage: int = Field(ge=0, le=8)
    windows: list[OutageWindow] = Field(default_factory=list)


class AreaOption(BaseModel):
    """A candidate area returned by an area search."""

    id: str
    name: str
    region: str | None = None


class Meeting(BaseModel):
    """A calendar event that may conflict with an outage."""

    id: str
    title: str
    start: datetime
    end: datetime
    is_online: bool = True


class Conflict(BaseModel):
    """A meeting that collides with an outage window."""

    meeting: Meeting
    outage: OutageWindow


class Alert(BaseModel):
    """A message surfaced to the human — only when it matters."""

    severity: Severity
    title: str
    body: str
    created_at: datetime = Field(default_factory=datetime.now)
