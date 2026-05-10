"""Orchestrates the full multi-agent email workflow."""

import copy
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from src.agents import (
    EmailCoachAgent,
    SuggestorAgent,
)
from src.models import AgentPipelineResult, EmailRequest
from src.prompts import UNIFIED_EMAIL_PROMPT
from src.utils import normalize_list, normalize_text, parse_json_response


# ── Default fallback values used when the model returns incomplete JSON ──

_DEFAULT_INTENT = {
    "intent": "general",
    "purpose_summary": "General professional communication request.",
    "confidence": 70,
    "reasoning": "Fallback output used because the model response was invalid.",
}

_DEFAULT_SITUATION = {
    "situation_summary": "Context is limited; focus on a professional and clear response.",
    "urgency_level": "medium",
    "relationship_context": "Professional communication",
    "risks": ["Potential misunderstanding due to missing context"],
    "recommended_focus": ["Be clear", "Be concise", "State next steps"],
}

_DEFAULT_STRATEGY = {
    "selected_strategy": "follow-up",
    "strategy_reason": "Follow-up is a safe default when additional context is limited.",
    "tactics": ["State the purpose early", "Provide clear context", "End with a direct next step"],
}

_DEFAULT_TONE = {
    "chosen_tone": "diplomatic",
    "tone_reason": "Tone selected to keep the email professional and effective.",
    "tone_rules": ["Use clear and respectful language", "Keep sentences concise", "Match tone to strategy"],
}

_DEFAULT_REVIEW = {
    "quality_score": 7,
    "quality_review": "The email is professional and clear, with minor room for tightening.",
    "strengths": ["Clear purpose", "Professional language"],
    "improvements": ["Tighten wording", "Make call to action explicit"],
    "final_subject_line": "",
    "final_email": "",
}

_DEFAULT_SIMULATION = {
    "predicted_reaction": {"positive": 33, "neutral": 33, "negative": 34},
    "risk_level": "medium",
    "risk_reasoning": "Standard professional communication has neutral risk.",
    "potential_objections": [],
}

ALLOWED_STRATEGIES = {"persuasion", "apology", "follow-up", "negotiation", "clarification"}
VALID_URGENCY = {"low", "medium", "high"}


class EmailAssistantOrchestrator:
    """Runs the entire email workflow in a SINGLE model call."""

    def __init__(self, llm: BaseChatModel) -> None:
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template(UNIFIED_EMAIL_PROMPT)

    def run(self, request: EmailRequest) -> AgentPipelineResult:
        """Execute the full pipeline with ONE model invocation."""

        num_versions = max(request.num_versions, 1)

        # ── Single LLM call ──
        messages = self.prompt.format_messages(
            email_purpose=request.email_purpose,
            recipient=request.recipient,
            situation=request.situation,
            key_points=request.key_points,
            tone_preference=normalize_text(request.tone_preference, "auto detect"),
            drafting_style=request.drafting_style,
            improve_existing_email=str(request.improve_existing_email).lower(),
            existing_email=request.existing_email,
            num_versions=num_versions,
        )
        response = self.llm.invoke(messages)
        raw_text = getattr(response, "content", "")
        if not isinstance(raw_text, str):
            raw_text = str(raw_text)

        # ── Parse the combined JSON ──
        full_default = {
            "intent": copy.deepcopy(_DEFAULT_INTENT),
            "situation_analysis": copy.deepcopy(_DEFAULT_SITUATION),
            "strategy": copy.deepcopy(_DEFAULT_STRATEGY),
            "tone": copy.deepcopy(_DEFAULT_TONE),
            "generated_email": {
                "subject_line": normalize_text(request.email_purpose, "Professional Update"),
                "email_draft": self._fallback_email(request),
            },
            "versions": [],
            "review": copy.deepcopy(_DEFAULT_REVIEW),
            "simulation": copy.deepcopy(_DEFAULT_SIMULATION),
        }
        result = parse_json_response(raw_text, full_default)

        # ── Normalize each section safely ──
        intent = self._normalize_intent(result.get("intent", {}), request)
        situation_analysis = self._normalize_situation(result.get("situation_analysis", {}), request)
        strategy = self._normalize_strategy(result.get("strategy", {}))
        tone = self._normalize_tone(result.get("tone", {}), request)
        generated_email = self._normalize_generated_email(result.get("generated_email", {}), request)
        review = self._normalize_review(result.get("review", {}), generated_email)
        simulation = self._normalize_simulation(result.get("simulation", {}))
        versions = self._normalize_versions(result.get("versions", []))

        final_subject = normalize_text(
            review.get("final_subject_line"),
            normalize_text(generated_email.get("subject_line"), "Professional Update"),
        )
        final_email = normalize_text(
            review.get("final_email"),
            normalize_text(generated_email.get("email_draft"), ""),
        )
        quality_review = normalize_text(
            review.get("quality_review"),
            "The email is ready with professional quality.",
        )

        return AgentPipelineResult(
            intent=intent,
            situation_analysis=situation_analysis,
            strategy=strategy,
            tone=tone,
            generated_email=generated_email,
            review=review,
            final_subject=final_subject,
            final_email=final_email,
            quality_review=quality_review,
            simulation=simulation,
            versions=versions if versions else None,
        )

    # ── Section normalizers ──

    @staticmethod
    def _normalize_intent(data: dict, request: EmailRequest) -> dict:
        default = copy.deepcopy(_DEFAULT_INTENT)
        default["purpose_summary"] = normalize_text(
            request.email_purpose, default["purpose_summary"]
        )
        if not isinstance(data, dict):
            return default
        data["intent"] = normalize_text(data.get("intent"), "general").lower()
        data["purpose_summary"] = normalize_text(data.get("purpose_summary"), default["purpose_summary"])
        data["reasoning"] = normalize_text(data.get("reasoning"), default["reasoning"])
        try:
            data["confidence"] = int(data.get("confidence", 70))
        except (TypeError, ValueError):
            data["confidence"] = 70
        return data

    @staticmethod
    def _normalize_situation(data: dict, request: EmailRequest) -> dict:
        default = copy.deepcopy(_DEFAULT_SITUATION)
        if not isinstance(data, dict):
            return default
        data["situation_summary"] = normalize_text(data.get("situation_summary"), default["situation_summary"])
        urgency = normalize_text(data.get("urgency_level"), "medium").lower()
        data["urgency_level"] = urgency if urgency in VALID_URGENCY else "medium"
        data["relationship_context"] = normalize_text(data.get("relationship_context"), default["relationship_context"])
        data["risks"] = normalize_list(data.get("risks")) or default["risks"]
        data["recommended_focus"] = normalize_list(data.get("recommended_focus")) or default["recommended_focus"]
        return data

    @staticmethod
    def _normalize_strategy(data: dict) -> dict:
        default = copy.deepcopy(_DEFAULT_STRATEGY)
        if not isinstance(data, dict):
            return default
        selected = normalize_text(data.get("selected_strategy"), "follow-up").lower()
        data["selected_strategy"] = selected if selected in ALLOWED_STRATEGIES else "follow-up"
        data["strategy_reason"] = normalize_text(data.get("strategy_reason"), default["strategy_reason"])
        data["tactics"] = normalize_list(data.get("tactics")) or default["tactics"]
        return data

    @staticmethod
    def _normalize_tone(data: dict, request: EmailRequest) -> dict:
        requested = normalize_text(request.tone_preference, "auto detect").lower()
        default_tone = "diplomatic" if requested == "auto detect" else requested
        default = copy.deepcopy(_DEFAULT_TONE)
        default["chosen_tone"] = default_tone
        if not isinstance(data, dict):
            return default
        data["chosen_tone"] = normalize_text(data.get("chosen_tone"), default_tone).lower()
        data["tone_reason"] = normalize_text(data.get("tone_reason"), default["tone_reason"])
        data["tone_rules"] = normalize_list(data.get("tone_rules")) or default["tone_rules"]
        return data

    @staticmethod
    def _normalize_generated_email(data: dict, request: EmailRequest) -> dict:
        fallback_subject = normalize_text(request.email_purpose, "Professional Update")
        if not isinstance(data, dict):
            return {"subject_line": fallback_subject, "email_draft": ""}
        data["subject_line"] = normalize_text(data.get("subject_line"), fallback_subject)
        data["email_draft"] = normalize_text(data.get("email_draft"), "")
        return data

    @staticmethod
    def _normalize_review(data: dict, generated_email: dict) -> dict:
        default = copy.deepcopy(_DEFAULT_REVIEW)
        default["final_subject_line"] = generated_email.get("subject_line", "")
        default["final_email"] = generated_email.get("email_draft", "")
        if not isinstance(data, dict):
            return default
        try:
            score = int(data.get("quality_score", 7))
        except (TypeError, ValueError):
            score = 7
        data["quality_score"] = max(1, min(score, 10))
        data["quality_review"] = normalize_text(data.get("quality_review"), default["quality_review"])
        data["strengths"] = normalize_list(data.get("strengths")) or default["strengths"]
        data["improvements"] = normalize_list(data.get("improvements")) or default["improvements"]
        data["final_subject_line"] = normalize_text(data.get("final_subject_line"), default["final_subject_line"])
        data["final_email"] = normalize_text(data.get("final_email"), default["final_email"])
        return data

    @staticmethod
    def _normalize_simulation(data: dict) -> dict:
        default = copy.deepcopy(_DEFAULT_SIMULATION)
        if not isinstance(data, dict):
            return default
        data.setdefault("predicted_reaction", default["predicted_reaction"])
        data.setdefault("risk_level", default["risk_level"])
        data.setdefault("risk_reasoning", default["risk_reasoning"])
        data.setdefault("potential_objections", default["potential_objections"])
        return data

    @staticmethod
    def _normalize_versions(data) -> list:
        if not isinstance(data, list):
            return []
        return [str(v).strip() for v in data if str(v).strip()]

    @staticmethod
    def _fallback_email(request: EmailRequest) -> str:
        recipient = normalize_text(request.recipient, "there")
        purpose = normalize_text(request.email_purpose, "Professional Update").lower()
        key_points = normalize_text(request.key_points, "Please find the key details below.")
        return (
            f"Dear {recipient},\n\n"
            f"I hope you are doing well. I am writing regarding {purpose}. "
            f"{key_points}\n\n"
            "Please let me know your thoughts.\n\n"
            "Best regards,\n"
            "[Your Name]"
        )
