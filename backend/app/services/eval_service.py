from __future__ import annotations

import re
from typing import Any

NORMALIZE_RE = re.compile(r"[^a-z0-9\s-]")


def _normalize(value: Any) -> str:
    text = str(value or "").lower()
    return " ".join(NORMALIZE_RE.sub(" ", text).split())


def validate_grounded_answer(
    answer: str,
    retrieved_schemes: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(answer, str) or not answer.strip():
        return {
            "valid": False,
            "reason": "Generated answer is empty or invalid.",
            "mentionedSchemes": [],
        }
    if not isinstance(retrieved_schemes, list):
        return {
            "valid": False,
            "reason": "Retrieved scheme context is invalid.",
            "mentionedSchemes": [],
        }

    normalized_answer = _normalize(answer)
    mentioned = []
    for scheme in retrieved_schemes:
        full_name = _normalize(scheme.get("name"))
        short_name = _normalize(scheme.get("short_name"))
        if (full_name and full_name in normalized_answer) or (
            short_name and short_name in normalized_answer
        ):
            mentioned.append(
                {
                    "id": scheme.get("id"),
                    "name": scheme.get("name"),
                    "short_name": scheme.get("short_name"),
                }
            )

    return {
        "valid": True,
        "reason": "Answer references the supplied retrieval context.",
        "mentionedSchemes": mentioned,
    }


def validate_recommended_scheme_ids(
    recommended_scheme_ids: list[str],
    retrieved_schemes: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(recommended_scheme_ids, list):
        return {
            "valid": False,
            "reason": "Recommended scheme IDs must be a list.",
            "invalidSchemeIds": [],
        }
    if not isinstance(retrieved_schemes, list):
        return {
            "valid": False,
            "reason": "Retrieved scheme context is invalid.",
            "invalidSchemeIds": [],
        }

    allowed_ids = {str(scheme.get("id")) for scheme in retrieved_schemes}
    invalid_ids = [
        scheme_id
        for scheme_id in recommended_scheme_ids
        if scheme_id not in allowed_ids
    ]

    return {
        "valid": not invalid_ids,
        "reason": (
            "All recommended scheme IDs are grounded in retrieved context."
            if not invalid_ids
            else "One or more recommended scheme IDs were not retrieved."
        ),
        "invalidSchemeIds": invalid_ids,
    }