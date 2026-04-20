"""Tone Selection Agent: selects and explains best tone."""

from typing import Any, Dict

from src.agents.base import BaseAgent
from src.models import EmailRequest
from src.prompts import TONE_SELECTION_PROMPT
from src.utils import normalize_list, normalize_text, to_json_string


class ToneSelectionAgent(BaseAgent):
    """Selects the most suitable tone based on strategy and context."""

    def __init__(self, llm) -> None:
        super().__init__(
            llm=llm,
            prompt_template=TONE_SELECTION_PROMPT,
            agent_name="Tone Selection Agent",
        )

    def run(
        self,
        request: EmailRequest,
        strategy_data: Dict[str, Any],
        situation_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run tone selection and normalize output."""

        requested_tone = normalize_text(request.tone_preference, "auto detect").lower()
        default_tone = "diplomatic" if requested_tone == "auto detect" else requested_tone

        default_output = {
            "chosen_tone": default_tone,
            "tone_reason": "Tone selected to keep the email professional and effective.",
            "tone_rules": [
                "Use clear and respectful language",
                "Keep sentences concise",
                "Match tone to the selected strategy",
            ],
        }

        result = self.invoke_json(
            default=default_output,
            tone_preference=requested_tone,
            recipient=request.recipient,
            strategy_json=to_json_string(strategy_data),
            situation_json=to_json_string(situation_data),
        )

        result["chosen_tone"] = normalize_text(result.get("chosen_tone"), default_tone).lower()
        result["tone_reason"] = normalize_text(
            result.get("tone_reason"),
            default_output["tone_reason"],
        )
        result["tone_rules"] = normalize_list(result.get("tone_rules")) or default_output["tone_rules"]

        return result
