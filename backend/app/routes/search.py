from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import SearchRequest
from app.services.retrieval_service import retrieve_relevant_schemes
from app.services.scheme_repository import scheme_repository

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("")
def search_schemes(payload: SearchRequest) -> dict:
    try:
        schemes = scheme_repository.load_all()
        results = retrieve_relevant_schemes(payload.query, schemes, limit=5, min_score=8)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=500, detail="Unable to search schemes.") from exc

    return {
        "query": payload.query,
        "count": len(results),
        "results": results,
    }