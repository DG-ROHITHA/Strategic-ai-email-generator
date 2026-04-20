"""Utility helpers for JSON parsing and text normalization."""

import copy
import json
import re
from typing import Any, Dict


def parse_json_response(raw_text: str, default: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a model response into JSON and fall back safely on failure."""

    if not raw_text:
        return copy.deepcopy(default)

    cleaned = raw_text.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    candidates = [cleaned]
    json_match = re.search(r"\{[\s\S]*\}", cleaned)
    if json_match:
        candidates.append(json_match.group(0))

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue

    return copy.deepcopy(default)


def to_json_string(data: Dict[str, Any]) -> str:
    """Pretty-print a dictionary before feeding it into another agent."""

    return json.dumps(data, indent=2, ensure_ascii=True)


def normalize_text(value: Any, fallback: str = "") -> str:
    """Normalize unknown values into clean strings."""

    text = str(value).strip() if value is not None else ""
    return text if text else fallback


def normalize_list(value: Any) -> list[str]:
    """Normalize unknown values into a list of non-empty strings."""

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str) and value.strip():
        return [value.strip()]

    return []
