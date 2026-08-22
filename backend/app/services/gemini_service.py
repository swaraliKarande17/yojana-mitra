from __future__ import annotations

import json

import httpx
from pydantic import ValidationError

from app.config import get_settings
from app.models import GeminiStructuredResponse


class GeminiServiceError(RuntimeError):
    pass


async def generate_structured_response(prompt: str) -> GeminiStructuredResponse:
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("A valid prompt is required.")

    settings = get_settings()
    if not settings.gemini_api_key:
        raise GeminiServiceError("GEMINI_API_KEY is not configured.")

    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt.strip()}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=settings.gemini_timeout_seconds) as client:
            response = await client.post(
                endpoint,
                params={"key": settings.gemini_api_key},
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:500]
        raise GeminiServiceError(
            f"Gemini request failed with status {exc.response.status_code}: {detail}"
        ) from exc
    except httpx.HTTPError as exc:
        raise GeminiServiceError(f"Gemini request failed: {exc}") from exc

    try:
        body = response.json()
        text = body["candidates"][0]["content"]["parts"][0]["text"].strip()
        parsed = json.loads(text)
        return GeminiStructuredResponse.model_validate(parsed)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError, ValidationError) as exc:
        raise GeminiServiceError("Gemini returned an invalid structured response.") from exc