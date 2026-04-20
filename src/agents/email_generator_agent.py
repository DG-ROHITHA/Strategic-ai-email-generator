"""Email Generator Agent: drafts the professional email."""

from typing import Any, Dict

from src.agents.base import BaseAgent
from src.models import EmailRequest
from src.prompts import EMAIL_GENERATOR_PROMPT
from src.utils import normalize_text, to_json_string


class EmailGeneratorAgent(BaseAgent):
    """Generates a subject line and polished email draft."""

    def __init__(self, llm) -> None:
        super().__init__(
            llm=llm,
            prompt_template=EMAIL_GENERATOR_PROMPT,
            agent_name="Email Generator Agent",
        )

    def run(
        self,
        request: EmailRequest,
        intent_data: Dict[str, Any],
        situation_data: Dict[str, Any],
        strategy_data: Dict[str, Any],
        tone_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate subject line and email draft."""

        fallback_subject = normalize_text(request.email_purpose, "Professional Update")
        fallback_recipient = normalize_text(request.recipient, "there")
        fallback_body = (
            f"Dear {fallback_recipient},\n\n"
            f"I hope you are doing well. I am writing regarding {fallback_subject.lower()}. "
            f"{normalize_text(request.key_points, 'Please find the key details below.')}\n\n"
            "Please let me know your thoughts.\n\n"
            "Best regards,\n"
            "[Your Name]"
        )

        default_output = {
            "subject_line": fallback_subject,
            "email_draft": fallback_body,
        }

        result = self.invoke_json(
            default=default_output,
            recipient=request.recipient,
            intent_json=to_json_string(intent_data),
            situation_json=to_json_string(situation_data),
            strategy_json=to_json_string(strategy_data),
            tone_json=to_json_string(tone_data),
            key_points=request.key_points,
            drafting_style=request.drafting_style,
            improve_existing_email=str(request.improve_existing_email).lower(),
            existing_email=request.existing_email,
        )

        result["subject_line"] = normalize_text(result.get("subject_line"), fallback_subject)
        result["email_draft"] = normalize_text(result.get("email_draft"), fallback_body)

        return result
