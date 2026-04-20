"""Outcome Simulator Agent: predicts recipient reaction and risks."""

from typing import Any, Dict
from src.agents.base import BaseAgent
from src.prompts import OUTCOME_SIMULATOR_PROMPT
from src.utils import to_json_string

class OutcomeSimulatorAgent(BaseAgent):
    """Predicts how the recipient will react to the email."""

    def __init__(self, llm) -> None:
        super().__init__(
            llm=llm,
            prompt_template=OUTCOME_SIMULATOR_PROMPT,
            agent_name="Outcome Simulator Agent",
        )

    def run(self, recipient: str, situation: str, email_content: str) -> Dict[str, Any]:
        """Run the simulation."""
        default_output = {
            "predicted_reaction": {"positive": 33, "neutral": 33, "negative": 34},
            "risk_level": "medium",
            "risk_reasoning": "Standard professional communication has neutral risk.",
            "potential_objections": []
        }

        return self.invoke_json(
            default=default_output,
            recipient=recipient,
            situation=situation,
            email_content=email_content
        )
