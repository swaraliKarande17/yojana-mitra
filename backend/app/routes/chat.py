from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import ChatRequest
from app.services.eval_service import (
    validate_grounded_answer,
    validate_recommended_scheme_ids,
)
from app.services.gemini_service import GeminiServiceError, generate_structured_response
from app.services.retrieval_service import retrieve_relevant_schemes
from app.services.scheme_repository import scheme_repository

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _build_grounded_prompt(user_query: str, schemes: list[dict]) -> str:
    blocks: list[str] = []
    for index, scheme in enumerate(schemes, start=1):
        eligibility = scheme.get("eligibility") or {}
        conditions = eligibility.get("important_conditions") or []
        condition_text = "\n".join(f"- {item}" for item in conditions) or "- Not available"
        categories = ", ".join(scheme.get("category") or [])
        target_groups = ", ".join(scheme.get("target_groups") or [])

        blocks.append(
            f"""SCHEME {index}
ID: {scheme.get('id')}
Name: {scheme.get('name')}
Short Name: {scheme.get('short_name')}
Category: {categories}
Target Groups: {target_groups}
Eligibility Summary: {eligibility.get('summary') or 'Not available'}

Important Conditions:
{condition_text}

Benefits: {scheme.get('benefits')}
Application Process: {scheme.get('application_process')}
Source: {scheme.get('official_source')}
"""
        )

    scheme_context = "\n".join(blocks)
    return f"""You are Yojana Mitra, an assistant that helps users discover Indian government welfare schemes.

STRICT RULES:
1. Answer ONLY using the scheme information provided below.
2. Do NOT invent any scheme.
3. Do NOT invent eligibility conditions, benefits, amounts, deadlines, or application processes.
4. Do NOT use general knowledge to recommend additional government schemes.
5. Do NOT claim that the user is definitely eligible unless the provided information proves it.
6. Use phrases such as \"may be eligible\" or \"may be relevant\" when eligibility is uncertain.
7. If important user information is missing, mention what information is required.
8. If none of the supplied schemes are relevant, clearly say so.
9. Keep the answer clear and practical.
10. Remind the user to verify final eligibility using the official government source.

OUTPUT RULES:
11. Return valid JSON only.
12. Return exactly these fields: \"answer\" and \"recommended_scheme_ids\".
13. Every ID in \"recommended_scheme_ids\" MUST come from the retrieved scheme data below.
14. Never invent a scheme ID.
15. If no scheme should be recommended, return an empty array.

USER QUESTION:
{user_query}

RETRIEVED SCHEME DATA:
{scheme_context}""".strip()


@router.post("")
async def chat(payload: ChatRequest) -> dict:
    try:
        schemes = scheme_repository.load_all()
        relevant = retrieve_relevant_schemes(payload.message, schemes, limit=5, min_score=8)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=500, detail="Unable to load scheme data.") from exc

    if not relevant:
        return {
            "answer": (
                "I could not find a sufficiently relevant scheme in the currently available "
                "scheme data. Please provide more details such as your occupation, age, state, "
                "income range, or the type of assistance you need."
            ),
            "grounding": {
                "valid": True,
                "recommendedSchemeIds": [],
                "mentionedSchemes": [],
            },
            "schemes": [],
        }

    try:
        llm_response = await generate_structured_response(
            _build_grounded_prompt(payload.message, relevant)
        )
    except (GeminiServiceError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="Unable to generate a grounded response.") from exc

    id_validation = validate_recommended_scheme_ids(
        llm_response.recommended_scheme_ids,
        relevant,
    )
    if not id_validation["valid"]:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Generated recommendations failed grounding validation.",
                "invalidSchemeIds": id_validation["invalidSchemeIds"],
            },
        )

    answer_validation = validate_grounded_answer(llm_response.answer, relevant)
    if not answer_validation["valid"]:
        raise HTTPException(status_code=502, detail="Generated answer failed grounding validation.")

    return {
        "answer": llm_response.answer,
        "grounding": {
            "valid": True,
            "recommendedSchemeIds": llm_response.recommended_scheme_ids,
            "mentionedSchemes": answer_validation["mentionedSchemes"],
        },
        "schemes": [
            {
                "id": scheme.get("id"),
                "name": scheme.get("name"),
                "short_name": scheme.get("short_name"),
                "score": scheme.get("score"),
                "official_source": scheme.get("official_source"),
            }
            for scheme in relevant
        ],
    }