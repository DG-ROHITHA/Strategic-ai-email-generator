"""Suggestor Agent: helps the user plan by suggesting points."""

from typing import Any, Dict
from src.agents.base import BaseAgent
from src.prompts import SUGGEST_POINTS_PROMPT

class SuggestorAgent(BaseAgent):
    """Suggests key points for an email purpose."""

    def __init__(self, llm) -> None:
        super().__init__(
            llm=llm,
            prompt_template=SUGGEST_POINTS_PROMPT,
            agent_name="Suggestor Agent",
        )

    def run(self, email_purpose: str, recipient: str) -> Dict[str, Any]:
        """Generate suggestions."""
        default_output = {
            "suggested_points": ["State the main request clearly", "Provide necessary context", "Outline next steps"],
            "recommended_strategy": "Be direct and professional."
        }

        return self.invoke_json(
            default=default_output,
            email_purpose=email_purpose,
            recipient=recipient
        )
