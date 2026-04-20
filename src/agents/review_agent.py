"""Email Review Agent: scores and refines draft quality."""

from typing import Any, Dict

from src.agents.base import BaseAgent
from src.models import EmailRequest
from src.prompts import EMAIL_REVIEW_PROMPT
from src.utils import normalize_list, normalize_text, to_json_string


class EmailReviewAgent(BaseAgent):
    """Reviews generated email and returns final polished version."""

    def __init__(self, llm) -> None:
        super().__init__(
            llm=llm,
            prompt_template=EMAIL_REVIEW_PROMPT,
            agent_name="Email Review Agent",
        )

    def run(
        self,
        request: EmailRequest,
        generated_email: Dict[str, Any],
        strategy_data: Dict[str, Any],
        tone_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Review, score, and optionally improve the draft."""

        subject_line = normalize_text(generated_email.get("subject_line"), "Professional Update")
        email_draft = normalize_text(generated_email.get("email_draft"), "")

        default_output = {
            "quality_score": 7,
            "quality_review": "The email is professional and clear, with minor room for tightening.",
            "strengths": ["Clear purpose", "Professional language"],
            "improvements": ["Tighten wording", "Make call to action explicit"],
            "final_subject_line": subject_line,
            "final_email": email_draft,
        }

        result = self.invoke_json(
            default=default_output,
            recipient=request.recipient,
            strategy_json=to_json_string(strategy_data),
            tone_json=to_json_string(tone_data),
            subject_line=subject_line,
            email_draft=email_draft,
        )

        try:
            score = int(result.get("quality_score", 7))
        except (TypeError, ValueError):
            score = 7
        result["quality_score"] = max(1, min(score, 10))

        result["quality_review"] = normalize_text(
            result.get("quality_review"),
            default_output["quality_review"],
        )
        result["strengths"] = normalize_list(result.get("strengths")) or default_output["strengths"]
        result["improvements"] = normalize_list(result.get("improvements")) or default_output[
            "improvements"
        ]
        result["final_subject_line"] = normalize_text(
            result.get("final_subject_line"),
            subject_line,
        )
        result["final_email"] = normalize_text(result.get("final_email"), email_draft)

        return result
