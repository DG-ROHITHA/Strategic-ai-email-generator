"""Strategy Selection Agent: picks communication strategy."""

from typing import Any, Dict

from src.agents.base import BaseAgent
from src.models import EmailRequest
from src.prompts import STRATEGY_SELECTION_PROMPT
from src.utils import normalize_list, normalize_text, to_json_string


class StrategySelectionAgent(BaseAgent):
    """Chooses one strategy from the allowed communication strategies."""

    ALLOWED_STRATEGIES = {
        "persuasion",
        "apology",
        "follow-up",
        "negotiation",
        "clarification",
    }

    def __init__(self, llm) -> None:
        super().__init__(
            llm=llm,
            prompt_template=STRATEGY_SELECTION_PROMPT,
            agent_name="Strategy Selection Agent",
        )

    def run(
        self,
        request: EmailRequest,
        intent_data: Dict[str, Any],
        situation_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Select communication strategy and normalize output."""

        default_output = {
            "selected_strategy": "follow-up",
            "strategy_reason": "Follow-up is a safe default when additional context is limited.",
            "tactics": [
                "State the purpose early",
                "Provide clear context",
                "End with a direct next step",
            ],
        }

        result = self.invoke_json(
            default=default_output,
            email_purpose=request.email_purpose,
            recipient=request.recipient,
            intent_json=to_json_string(intent_data),
            situation_json=to_json_string(situation_data),
        )

        selected_strategy = normalize_text(result.get("selected_strategy"), "follow-up").lower()
        if selected_strategy not in self.ALLOWED_STRATEGIES:
            selected_strategy = "follow-up"

        result["selected_strategy"] = selected_strategy
        result["strategy_reason"] = normalize_text(
            result.get("strategy_reason"),
            default_output["strategy_reason"],
        )
        result["tactics"] = normalize_list(result.get("tactics")) or default_output["tactics"]

        return result
