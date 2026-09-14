"""FastAPI application — HTTP surface over the CandleFree agent and services."""

from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from candlefree.agent.container import get_container
from candlefree.agent.factory import AgentFactory
from candlefree.domain.models import Alert, AreaOption, AreaSchedule, Conflict, Meeting

app = FastAPI(title="CandleFree", description="Autonomous load shedding life-manager agent")

_STATIC = Path(__file__).parent / "static"


class AgentRunResult(BaseModel):
    summary: str
    alerts: list[Alert]
    meetings: list[Meeting]
    conflicts: list[Conflict]
    schedule: AreaSchedule


class AreaUpdate(BaseModel):
    area_id: str


@app.get("/area")
def get_area() -> dict[str, str]:
    return {"area_id": get_container().area_id}


@app.post("/area")
def set_area(update: AreaUpdate) -> dict[str, str]:
    """Change the monitored area at runtime (ESP area id, or any name in demo mode)."""
    c = get_container()
    c.state["area_id"] = update.area_id.strip()
    return {"area_id": c.area_id}


@app.get("/area/search", response_model=list[AreaOption])
def search_area(q: str) -> list[AreaOption]:
    """Search live ESP areas (returns [] in demo mode — UI falls back to OpenStreetMap)."""
    return get_container().provider.search_areas(q)


@app.post("/demo/reset")
def demo_reset() -> dict[str, str]:
    """Reset demo state (fresh schedule, meetings, and alerts)."""
    get_container.cache_clear()
    return {"status": "reset"}


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(_STATIC / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/meetings", response_model=list[Meeting])
def meetings() -> list[Meeting]:
    c = get_container()
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return c.calendar.get_meetings(now, now + timedelta(days=2))


@app.get("/schedule", response_model=AreaSchedule)
def schedule() -> AreaSchedule:
    c = get_container()
    return c.conflict_service.get_schedule(c.area_id)


@app.get("/conflicts", response_model=list[Conflict])
def conflicts() -> list[Conflict]:
    c = get_container()
    return c.conflict_service.find_conflicts(c.area_id)


@app.post("/agent/run", response_model=AgentRunResult)
def run_agent() -> AgentRunResult:
    """Trigger one autonomous background pass of the agent."""
    c = get_container()
    agent = AgentFactory.create()
    result = agent(
        "Run your background check now: inspect the schedule, resolve any meeting "
        "conflicts autonomously, and alert the user only if needed."
    )
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return AgentRunResult(
        summary=str(result),
        alerts=list(getattr(c.notifier, "sent", [])),
        meetings=c.calendar.get_meetings(now, now + timedelta(days=2)),
        conflicts=c.conflict_service.find_conflicts(c.area_id),
        schedule=c.conflict_service.get_schedule(c.area_id),
    )


@app.get("/alerts", response_model=list[Alert])
def alerts() -> list[Alert]:
    c = get_container()
    return list(getattr(c.notifier, "sent", []))

