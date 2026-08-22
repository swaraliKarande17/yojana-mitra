from app.services.retrieval_service import retrieve_relevant_schemes
from app.services.scheme_repository import scheme_repository


def test_crop_insurance_ranking():
    results = retrieve_relevant_schemes(
        "I am a farmer and I need crop insurance",
        scheme_repository.load_all(),
        limit=5,
        min_score=8,
    )
    assert [item["id"] for item in results[:3]] == [
        "pm-fasal-bima-yojana",
        "kisan-credit-card",
        "pm-kisan",
    ]


def test_scholarship_ranking():
    results = retrieve_relevant_schemes(
        "I am a student looking for scholarship",
        scheme_repository.load_all(),
        limit=5,
        min_score=8,
    )
    assert results
    assert results[0]["id"] == "nsp"