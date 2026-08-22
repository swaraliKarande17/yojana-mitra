from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.scheme_repository import scheme_repository

router = APIRouter(prefix="/api/schemes", tags=["schemes"])


@router.get("")
def list_schemes() -> dict:
    try:
        schemes = scheme_repository.load_all()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail="Unable to load scheme data.") from exc
    return {"count": len(schemes), "schemes": schemes}


@router.get("/{scheme_id}")
def get_scheme(scheme_id: str) -> dict:
    try:
        scheme = scheme_repository.get_by_id(scheme_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail="Unable to load scheme data.") from exc
    if scheme is None:
        raise HTTPException(status_code=404, detail="Scheme not found.")
    return {"scheme": scheme}