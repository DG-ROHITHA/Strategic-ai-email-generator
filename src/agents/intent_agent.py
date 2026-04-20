"""Intent Agent: detects the core email purpose."""

from typing import Any, Dict

from src.agents.base import BaseAgent
from src.models import EmailRequest
from src.prompts import INTENT_AGENT_PROMPT
from src.utils import normalize_text


class IntentAgent(BaseAgent):
    """Detects user intent from the request context."""

    def __init__(self, llm) -> None:
        super().__init__(
            llm=llm,
            prompt_template=INTENT_AGENT_PROMPT,
            agent_name="Intent Agent",
        )

    def run(self, request: EmailRequest) -> Dict[str, Any]:
        """Run intent classification and return structured output."""

        default_output = {
            "intent": "general",
            "purpose_summary": normalize_text(
                request.email_purpose,
                "General professional communication request.",
            ),
            "confidence": 70,
            "reasoning": "Fallback output used because the model response was invalid.",
        }

        result = self.invoke_json(
            default=default_output,
            email_purpose=request.email_purpose,
            situation=request.situation,
            key_points=request.key_points,
        )

        result["intent"] = normalize_text(result.get("intent"), "general").lower()
        result["purpose_summary"] = normalize_text(
            result.get("purpose_summary"),
            default_output["purpose_summary"],
        )
        result["reasoning"] = normalize_text(
            result.get("reasoning"),
            default_output["reasoning"],
        )

        try:
            result["confidence"] = int(result.get("confidence", 70))
        except (TypeError, ValueError):
            result["confidence"] = 70

        return result
