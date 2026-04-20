"""Email Coach Agent: provides live feedback on drafting."""

from typing import Any, Dict
from src.agents.base import BaseAgent
from src.prompts import EMAIL_COACH_PROMPT

class EmailCoachAgent(BaseAgent):
    """Provides real-time feedback while the user types."""

    def __init__(self, llm) -> None:
        super().__init__(
            llm=llm,
            prompt_template=EMAIL_COACH_PROMPT,
            agent_name="Email Coach Agent",
        )

    def run(self, current_draft: str, recipient: str, intent: str) -> Dict[str, Any]:
        """Produce live feedback."""
        default_output = {
            "tone_check": "Analyzing...",
            "is_too_aggressive": False,
            "suggestions": [],
            "improved_sentence": ""
        }

        return self.invoke_json(
            default=default_output,
            current_draft=current_draft,
            recipient=recipient,
            intent=intent
        )
