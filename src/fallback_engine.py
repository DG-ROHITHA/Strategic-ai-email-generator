"""Local fallback engine for offline or quota-limited email generation."""

import re

from src.models import AgentPipelineResult, EmailRequest
from src.utils import normalize_text


def _extract_key_points(raw_points: str) -> list[str]:
    """Split key points text into a clean list of bullet-like items."""

    if not raw_points.strip():
        return ["Share a clear next step."]

    normalized = raw_points.replace("\r\n", "\n").replace("\r", "\n")
    chunks = []
    for line in normalized.split("\n"):
        line = line.strip(" -\t")
        if not line:
            continue
        for part in line.split(";"):
            cleaned = part.strip(" -\t")
            if cleaned:
                chunks.append(cleaned)

    return chunks or ["Share a clear next step."]


def _detect_strategy(email_purpose: str, situation: str) -> str:
    """Choose a strategy using simple keyword rules."""

    text = f"{email_purpose} {situation}".lower()

    # Prioritize extension/cost discussion over apology when both appear.
    if any(word in text for word in ["negot", "budget", "price", "cost", "discount", "extension"]):
        return "negotiation"
    if any(word in text for word in ["clarify", "clarification", "confus", "question", "explain"]):
        return "clarification"
    if any(word in text for word in ["follow up", "follow-up", "reminder", "pending", "status"]):
        return "follow-up"
    if any(word in text for word in ["sorry", "apolog", "delay", "missed"]):
        return "apology"
    return "persuasion"


def _detect_tone(user_tone_preference: str, strategy: str) -> str:
    """Resolve tone preference with strategy-aware defaults."""

    preference = normalize_text(user_tone_preference, "auto detect").lower()
    if preference and preference != "auto detect":
        return preference

    mapping = {
        "apology": "empathetic",
        "follow-up": "concise",
        "negotiation": "diplomatic",
        "clarification": "professional",
        "persuasion": "confident",
    }
    return mapping.get(strategy, "professional")


def _generate_subject(strategy: str, purpose: str) -> str:
    """Create a professional subject line."""

    short_purpose = normalize_text(purpose, "Professional Update").strip().rstrip(".")

    if strategy == "apology":
        return f"Apology and Next Steps: {short_purpose}"
    if strategy == "follow-up":
        return f"Follow-Up: {short_purpose}"
    if strategy == "negotiation":
        return f"Proposal Discussion: {short_purpose}"
    if strategy == "clarification":
        return f"Clarification Needed: {short_purpose}"
    return f"Request: {short_purpose}"


def _naturalize_context(context: str) -> str:
    """Convert shorthand context text into a cleaner sentence."""

    text = context.strip().rstrip(".")
    if not text:
        return ""

    lower_text = text.lower()
    if lower_text.startswith("due to "):
        rest = text[7:].strip()
        rest = re.sub(r"\bgot delayed\b", "has been delayed", rest, flags=re.IGNORECASE)
        rest = re.sub(r"\bproject completion\b", "project completion", rest, flags=re.IGNORECASE)
        rest = re.sub(r"\bissue\s+project\b", "issue, project", rest, flags=re.IGNORECASE)
        if rest and not rest.lower().startswith(("a ", "an ", "the ")):
            rest = f"a {rest}"
        return f"Due to {rest}."

    return text[:1].upper() + text[1:] + "."


def _naturalize_point(point: str) -> str:
    """Convert shorthand key point into a natural request phrase."""

    text = point.strip().rstrip(".")
    if not text:
        return ""

    lower_text = text.lower()
    if lower_text.startswith("ask for "):
        text = text[8:].strip()
    elif lower_text.startswith("request "):
        text = text[8:].strip()

    text = re.sub(r"\b(\d+)\s+days\s+extension\b", r"a \1-day extension", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(\d+)\s+day\s+extension\b", r"a \1-day extension", text, flags=re.IGNORECASE)

    return text


def _point_to_request_sentence(point: str) -> str:
    """Turn a normalized point into a natural request sentence."""

    lower_point = point.lower().strip()
    if not lower_point:
        return ""

    if lower_point.startswith(("a ", "an ", "the ", "my ", "our ")):
        return f"Specifically, I would like to request {lower_point}."

    if lower_point.startswith(
        ("approve ", "consider ", "provide ", "share ", "review ", "confirm ", "grant ", "extend ", "schedule ", "allow ")
    ):
        return f"Specifically, I would like you to {lower_point}."

    return f"Specifically, I would like to {lower_point}."


def _build_email_body(
    request: EmailRequest,
    strategy: str,
    tone: str,
    points: list[str],
) -> str:
    """Construct a clean professional email draft from heuristic decisions."""

    recipient = normalize_text(request.recipient, "there")
    purpose = normalize_text(request.email_purpose, "this matter")
    situation = normalize_text(request.situation, "")

    purpose_text = purpose.strip().rstrip(".")
    if purpose_text.lower().startswith("request "):
        purpose_text = purpose_text[8:].strip()
    purpose_text = re.sub(r"\bfor client\b", "for the client", purpose_text, flags=re.IGNORECASE)

    strategy_openers = {
        "apology": "I sincerely apologize for the inconvenience related to",
        "follow-up": "I am writing to follow up on",
        "negotiation": "I am writing to discuss",
        "clarification": "I am writing to clarify",
        "persuasion": "I am writing regarding",
    }

    opener = strategy_openers.get(strategy, "I am writing regarding")

    intro = f"{opener} {purpose_text}."
    context_line = ""
    if situation:
        context_line = _naturalize_context(situation)

    cleaned_points = [_naturalize_point(point) for point in points if point.strip()]
    cleaned_points = [point for point in cleaned_points if point]
    if not cleaned_points:
        cleaned_points = ["share the next steps clearly"]

    if len(cleaned_points) == 1:
        points_line = _point_to_request_sentence(cleaned_points[0])
    else:
        joined = "; ".join(cleaned_points)
        points_line = f"To move this forward, I would like to highlight: {joined}."

    closing_lines = {
        "apology": "Thank you for your patience and understanding.",
        "follow-up": "I would appreciate your update when convenient.",
        "negotiation": "Please let me know if this approach works from your side.",
        "clarification": "Please let me know if any part needs further clarification.",
        "persuasion": "Please let me know your thoughts when convenient.",
    }
    closing_line = closing_lines.get(strategy, "Please let me know your thoughts when convenient.")

    body = [
        f"Dear {recipient},",
        "",
        intro,
    ]

    if context_line:
        body.extend(["", context_line])

    body.extend(
        [
            "",
            points_line,
            "",
            closing_line,
            "",
            "Best regards,",
            "[Your Name]",
        ]
    )

    return "\n".join(body)


def _build_review(strategy: str, tone: str) -> tuple[int, str, list[str], list[str]]:
    """Return a simple deterministic quality review."""

    strengths = [
        "Clear purpose and structure",
        f"Tone is aligned with a {strategy} strategy",
        "Contains explicit next-step request",
    ]
    improvements = [
        "Add specific date/time if a deadline is critical",
        "Personalize one sentence for the recipient relationship",
    ]
    review = (
        "This draft is professionally structured, readable, and action-oriented. "
        f"The tone is {tone} and suitable for business communication."
    )
    return 8, review, strengths, improvements


def generate_fallback_result(request: EmailRequest) -> AgentPipelineResult:
    """Generate a complete pipeline result without external LLM calls."""

    strategy = _detect_strategy(request.email_purpose, request.situation)
    tone = _detect_tone(request.tone_preference, strategy)
    key_points = _extract_key_points(request.key_points)

    intent_data = {
        "intent": normalize_text(request.email_purpose, "general communication").lower(),
        "purpose_summary": normalize_text(request.email_purpose, "General professional communication request."),
        "confidence": 65,
        "reasoning": "Rule-based fallback classification was used.",
    }

    situation_data = {
        "situation_summary": normalize_text(request.situation, "Context is limited; keep communication clear."),
        "urgency_level": "medium",
        "relationship_context": "Professional communication",
        "risks": ["Potential misunderstanding if details are incomplete"],
        "recommended_focus": ["clarity", "politeness", "next steps"],
    }

    strategy_data = {
        "selected_strategy": strategy,
        "strategy_reason": "Selected via fallback keyword analysis and context matching.",
        "tactics": [
            "State purpose in first line",
            "Provide concise supporting context",
            "End with a clear action request",
        ],
    }

    tone_data = {
        "chosen_tone": tone,
        "tone_reason": "Derived from user preference and selected strategy.",
        "tone_rules": [
            "Use respectful language",
            "Keep sentences concise",
            "Avoid ambiguity",
        ],
    }

    subject = _generate_subject(strategy, request.email_purpose)
    draft = _build_email_body(request, strategy, tone, key_points)

    generated_email_data = {
        "subject_line": subject,
        "email_draft": draft,
    }

    quality_score, quality_review, strengths, improvements = _build_review(strategy, tone)
    review_data = {
        "quality_score": quality_score,
        "quality_review": quality_review,
        "strengths": strengths,
        "improvements": improvements,
        "final_subject_line": subject,
        "final_email": draft,
    }

    return AgentPipelineResult(
        intent=intent_data,
        situation_analysis=situation_data,
        strategy=strategy_data,
        tone=tone_data,
        generated_email=generated_email_data,
        review=review_data,
        final_subject=subject,
        final_email=draft,
        quality_review=quality_review,
    )
