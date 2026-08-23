from app.sources.data_gov_source import DataGovSource


def test_data_gov_normalization():
    source = DataGovSource(
        resource_id="test-resource-id",
        api_key="",
        scheme_id="pm-kisan",
        scheme_name="PM-KISAN",
        official_source_url=(
            "https://data.gov.in/catalog/"
            "pm-kisan-scheme"
        ),
        category=["Agriculture"],
        target_groups=["Farmer"],
        keywords=["farmer", "pm kisan"],
    )

    result = source.normalize(
        {
            "records": [
                {
                    "state": "Maharashtra",
                    "beneficiaries": "100",
                }
            ],
            "total": 1,
        }
    )

    assert result["id"] == "pm-kisan"
    assert result["name"] == "PM-KISAN"

    assert (
        result["source"]["authority"]
        .startswith("National Informatics Centre")
    )

    assert result["official_data"]["record_count"] == 1