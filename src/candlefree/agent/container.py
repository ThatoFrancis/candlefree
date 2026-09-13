"""Composition root: wires concrete implementations to abstractions (DI container)."""

from dataclasses import dataclass
from functools import lru_cache

from candlefree.config import Settings, get_settings
from candlefree.interfaces.calendar_service import CalendarService
from candlefree.interfaces.notifier import Notifier
from candlefree.interfaces.schedule_provider import LoadSheddingProvider
from candlefree.providers.esp_provider import EskomSePushProvider
from candlefree.providers.mocks import ConsoleNotifier, MockCalendarService, MockLoadSheddingProvider
from candlefree.services.conflict_service import ConflictService


@dataclass(frozen=True)
class Container:
    settings: Settings
    provider: LoadSheddingProvider
    calendar: CalendarService
    notifier: Notifier
    conflict_service: ConflictService
    # Mutable runtime state (frozen dataclass holds the reference, dict contents may change)
    state: dict = None

    @property
    def area_id(self) -> str:
        return self.state["area_id"]


@lru_cache
def get_container() -> Container:
    settings = get_settings()
    provider: LoadSheddingProvider
    if settings.demo_mode or not settings.esp_api_key:
        provider = MockLoadSheddingProvider()
    else:
        provider = EskomSePushProvider(settings.esp_api_key, settings.esp_base_url)
    calendar: CalendarService = MockCalendarService()
    notifier: Notifier = ConsoleNotifier()
    demo = settings.demo_mode or not settings.esp_api_key
    initial_area = "Fourways Ext 10, Johannesburg" if demo else settings.esp_area_id
    return Container(
        settings=settings,
        provider=provider,
        calendar=calendar,
        notifier=notifier,
        conflict_service=ConflictService(provider, calendar),
        state={"area_id": initial_area},
    )
