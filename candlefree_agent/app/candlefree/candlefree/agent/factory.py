"""Factory that assembles the CandleFree Strands agent."""

from strands import Agent
from strands.models import BedrockModel

from candlefree.agent import tools
from candlefree.config import get_settings

SYSTEM_PROMPT = """You are CandleFree, an autonomous load shedding life-manager for a user in South Africa.

Your job runs in the background. On each run:
1. Check the load shedding schedule for the user's area.
2. Find online meetings that clash with outages in the next 24 hours.
3. For each conflict, work out the earliest power-safe slot and reschedule the meeting.
4. Notify the user ONLY when something matters: a meeting was moved (severity 'warning',
   include old time, new time, and why), or a decision is genuinely needed
   (severity 'decision_required'). If nothing clashes, do NOT notify — stay silent.

Be decisive: reschedule autonomously using the suggested safe slot; the user has pre-approved this.
Keep alerts short, friendly, and specific (South African context: stages, Eskom, etc.).
"""


class AgentFactory:
    """Builds configured CandleFree agents (Open/Closed: extend via new tools)."""

    @staticmethod
    def create() -> Agent:
        settings = get_settings()
        model = BedrockModel(
            model_id=settings.model_id,
            region_name=settings.bedrock_region,
            max_tokens=2048,
        )
        return Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            # No console streaming: robust on non-UTF-8 terminals (Windows cp1252);
            # results are returned from the call and surfaced via the Notifier.
            callback_handler=None,
            tools=[
                tools.get_loadshedding_schedule,
                tools.find_meeting_conflicts,
                tools.suggest_safe_slot,
                tools.reschedule_meeting,
                tools.notify_user,
            ],
        )
