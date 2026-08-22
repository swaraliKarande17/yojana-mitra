from __future__ import annotations

import json
import re
from typing import Any

STOP_WORDS = {
    "i", "am", "a", "an", "the", "and", "or", "but", "to", "for", "of",
    "in", "on", "with", "my", "me", "we", "our", "is", "are", "was",
    "were", "be", "been", "being", "need", "want", "looking", "get",
    "have", "has", "had",
}

TOKEN_RE = re.compile(r"[^a-z0-9\s-]")


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(map(str, value)).lower()
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False).lower()
    return str(value).lower()


def _tokenize(text: Any) -> list[str]:
    cleaned = TOKEN_RE.sub(" ", _normalize_text(text))
    return [
        token
        for token in cleaned.split()
        if len(token) >= 3 and token not in STOP_WORDS
    ]


def _count_matches(query_tokens: list[str], value: Any) -> int:
    searchable_tokens = set(_tokenize(value))
    return sum(1 for token in query_tokens if token in searchable_tokens)


def _score_scheme(query_tokens: list[str], scheme: dict[str, Any]) -> int:
    return (
        _count_matches(query_tokens, scheme.get("name")) * 6
        + _count_matches(query_tokens, scheme.get("short_name")) * 6
        + _count_matches(query_tokens, scheme.get("keywords")) * 5
        + _count_matches(query_tokens, scheme.get("target_groups")) * 4
        + _count_matches(query_tokens, scheme.get("category")) * 4
        + _count_matches(query_tokens, scheme.get("eligibility")) * 2
        + _count_matches(query_tokens, scheme.get("benefits")) * 2
    )


def retrieve_relevant_schemes(
    query: str,
    schemes: list[dict[str, Any]],
    limit: int = 5,
    min_score: int = 8,
) -> list[dict[str, Any]]:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("A valid search query is required.")
    if not isinstance(schemes, list):
        raise ValueError("Scheme data must be a list.")
    if limit < 1:
        raise ValueError("limit must be at least 1.")

    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    scored: list[dict[str, Any]] = []
    for scheme in schemes:
        score = _score_scheme(query_tokens, scheme)
        if score >= min_score:
            scored.append({**scheme, "score": score})

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:limit]