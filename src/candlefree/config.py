"""Application configuration (12-factor, environment driven)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central, validated application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="CANDLEFREE_", extra="ignore")

    app_name: str = "CandleFree"
    environment: str = "dev"

    # EskomSePush API (https://eskomsepush.gumroad.com/l/api)
    esp_api_key: str = ""
    esp_base_url: str = "https://developer.sepush.co.za/business/2.0"
    esp_area_id: str = "eskde-10-fourwaysext10cityofjohannesburggauteng"

    # When true, mock providers are used (no external API calls) — ideal for demos/tests.
    demo_mode: bool = True

    # Strands / Bedrock model
    model_id: str = "global.anthropic.claude-sonnet-4-6"
    bedrock_region: str = "us-east-1"

    # Minutes of warning the user wants before an outage.
    alert_lead_time_minutes: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
