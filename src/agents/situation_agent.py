"""Situation Analysis Agent: understands context and risk."""

from typing import Any, Dict

from src.agents.base import BaseAgent
from src.models import EmailRequest
from src.prompts import SITUATION_ANALYSIS_PROMPT
from src.utils import normalize_list, normalize_text, to_json_string


class SituationAnalysisAgent(BaseAgent):
    """Analyzes the situation and extracts planning signals."""

    VALID_URGENCY = {"low", "medium", "high"}

    def __init__(self, llm) -> None:
        super().__init__(
            llm=llm,
            prompt_template=SITUATION_ANALYSIS_PROMPT,
            agent_name="Situation Analysis Agent",
        )

    def run(self, request: EmailRequest, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run situation analysis and normalize output."""

        default_output = {
            "situation_summary": normalize_text(
                request.situation,
                "Context is limited; focus on a professional and clear response.",
            ),
            "urgency_level": "medium",
            "relationship_context": "Professional communication",
            "risks": ["Potential misunderstanding due to missing context"],
            "recommended_focus": ["Be clear", "Be concise", "State next steps"],
        }

        result = self.invoke_json(
            default=default_output,
            intent_json=to_json_string(intent_data),
            situation=request.situation,
            key_points=request.key_points,
        )

        result["situation_summary"] = normalize_text(
            result.get("situation_summary"),
            default_output["situation_summary"],
        )

        urgency = normalize_text(result.get("urgency_level"), "medium").lower()
        result["urgency_level"] = urgency if urgency in self.VALID_URGENCY else "medium"

        result["relationship_context"] = normalize_text(
            result.get("relationship_context"),
            default_output["relationship_context"],
        )
        result["risks"] = normalize_list(result.get("risks")) or default_output["risks"]
        result["recommended_focus"] = normalize_list(result.get("recommended_focus")) or default_output[
            "recommended_focus"
        ]

        return result
