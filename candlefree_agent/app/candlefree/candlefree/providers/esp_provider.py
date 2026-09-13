"""EskomSePush API implementation of LoadSheddingProvider."""

from datetime import datetime

import httpx

from candlefree.domain.models import AreaOption, AreaSchedule, OutageWindow
from candlefree.interfaces.schedule_provider import LoadSheddingProvider


class EskomSePushProvider(LoadSheddingProvider):
    """Fetches live schedules from the EskomSePush (ESP) API."""

    def __init__(self, api_key: str, base_url: str, timeout: float = 10.0) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def get_schedule(self, area_id: str) -> AreaSchedule:
        data = self._fetch_area(area_id)
        windows = [
            OutageWindow(
                stage=int(event["note"].replace("Stage ", "") or 0),
                start=datetime.fromisoformat(event["start"]),
                end=datetime.fromisoformat(event["end"]),
            )
            for event in data.get("events", [])
        ]
        current_stage = windows[0].stage if windows else 0
        return AreaSchedule(
            area_id=area_id,
            area_name=data.get("info", {}).get("name", area_id),
            current_stage=current_stage,
            windows=windows,
        )

    def search_areas(self, text: str) -> list[AreaOption]:
        response = httpx.get(
            f"{self._base_url}/areas_search",
            params={"text": text},
            headers={"token": self._api_key},
            timeout=self._timeout,
        )
        response.raise_for_status()
        return [
            AreaOption(id=a["id"], name=a["name"], region=a.get("region"))
            for a in response.json().get("areas", [])
        ]

    def _fetch_area(self, area_id: str) -> dict:
        response = httpx.get(
            f"{self._base_url}/area",
            params={"id": area_id},
            headers={"token": self._api_key},
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()
