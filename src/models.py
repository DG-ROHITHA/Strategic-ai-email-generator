"""Data models used across the multi-agent email assistant."""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class EmailRequest:
    """User input payload for the email generation workflow."""

    email_purpose: str
    recipient: str
    situation: str
    tone_preference: str
    key_points: str
    drafting_style: str = "balanced"  # OPTIONS: "concise", "detailed", "balanced"
    improve_existing_email: bool = False
    existing_email: str = ""
    num_versions: int = 1


@dataclass
class AgentPipelineResult:
    """Final output plus intermediate agent decisions for transparency."""

    intent: Dict[str, Any]
    situation_analysis: Dict[str, Any]
    strategy: Dict[str, Any]
    tone: Dict[str, Any]
    generated_email: Dict[str, Any]
    review: Dict[str, Any]
    final_subject: str
    final_email: str
    quality_review: str
    simulation: Optional[Dict[str, Any]] = None
    versions: Optional[list[str]] = None
