from app.services.eval_service import validate_recommended_scheme_ids


def test_rejects_unknown_scheme_id():
    result = validate_recommended_scheme_ids(
        ["pm-fasal-bima-yojana", "fake-government-scheme"],
        [{"id": "pm-fasal-bima-yojana"}],
    )
    assert result["valid"] is False
    assert result["invalidSchemeIds"] == ["fake-government-scheme"]