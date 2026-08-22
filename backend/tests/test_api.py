from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Yojana Mitra API"}


def test_scheme_count():
    response = client.get("/api/schemes")
    assert response.status_code == 200
    assert response.json()["count"] == 20


def test_scheme_by_id():
    response = client.get("/api/schemes/pm-kisan")
    assert response.status_code == 200
    assert response.json()["scheme"]["id"] == "pm-kisan"


def test_missing_scheme():
    response = client.get("/api/schemes/does-not-exist")
    assert response.status_code == 404


def test_search():
    response = client.post(
        "/api/search",
        json={"query": "I am pregnant and need maternity support"},
    )
    assert response.status_code == 200
    ids = [item["id"] for item in response.json()["results"]]
    assert ids[:2] == ["pmmvy", "janani-suraksha-yojana"]


def test_chat_with_grounded_mock(monkeypatch):
    from app.models import GeminiStructuredResponse
    import app.routes.chat as chat_module

    async def fake_generate(_prompt: str):
        return GeminiStructuredResponse(
            answer="Pradhan Mantri Fasal Bima Yojana (PMFBY) may be relevant for crop insurance.",
            recommended_scheme_ids=["pm-fasal-bima-yojana"],
        )

    monkeypatch.setattr(chat_module, "generate_structured_response", fake_generate)
    response = client.post(
        "/api/chat",
        json={"message": "I am a farmer and I need crop insurance"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["grounding"]["valid"] is True
    assert body["grounding"]["recommendedSchemeIds"] == ["pm-fasal-bima-yojana"]


def test_chat_rejects_unretrieved_scheme_id(monkeypatch):
    from app.models import GeminiStructuredResponse
    import app.routes.chat as chat_module

    async def fake_generate(_prompt: str):
        return GeminiStructuredResponse(
            answer="A fake scheme may help.",
            recommended_scheme_ids=["fake-government-scheme"],
        )

    monkeypatch.setattr(chat_module, "generate_structured_response", fake_generate)
    response = client.post(
        "/api/chat",
        json={"message": "I am a farmer and I need crop insurance"},
    )
    assert response.status_code == 502