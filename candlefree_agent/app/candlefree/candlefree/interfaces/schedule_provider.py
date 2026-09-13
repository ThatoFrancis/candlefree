"""Abstraction over load shedding data sources (Dependency Inversion)."""

from abc import ABC, abstractmethod

from candlefree.domain.models import AreaOption, AreaSchedule


class LoadSheddingProvider(ABC):
    """Any source of load shedding schedules (EskomSePush, mock, cache...)."""

    @abstractmethod
    def get_schedule(self, area_id: str) -> AreaSchedule:
        """Return the current stage and upcoming outage windows for an area."""

    @abstractmethod
    def search_areas(self, text: str) -> list[AreaOption]:
        """Find candidate areas matching a free-text query (empty if unsupported)."""
