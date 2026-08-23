import json

import pytest

from app.services.source_ingestion_service import SourceIngestionService
from app.sources.base_source import GovernmentSource


class FakeGovernmentSource(GovernmentSource):
    source_name = "Fake Official Source"
    authority = "Government Test Authority"

    async def fetch_schemes(self):
        raw_item = {
            "id": "test-scheme",
            "name": "Test Government Scheme",
        }

        return [self.normalize(raw_item)]

    def normalize(self, raw_item):
        return {
            "id": raw_item["id"],
            "name": raw_item["name"],
            "short_name": "TEST",
            "category": ["Testing"],
            "target_groups": ["Citizen"],
            "eligibility": {},
            "benefits": "Testing benefit.",
            "application_process": "Testing only.",
            "keywords": ["test"],
            "source": {
                "authority": self.authority,
                "source_name": self.source_name,
                "url": "https://data.gov.in/",
                "fetched_at": "2026-08-23T00:00:00+00:00",
            },
        }


@pytest.mark.asyncio
async def test_ingestion_writes_official_cache(tmp_path):
    cache_file = tmp_path / "official_scheme_cache.json"

    service = SourceIngestionService(
        cache_path=cache_file
    )

    result = await service.ingest(
        [FakeGovernmentSource()]
    )

    assert len(result) == 1
    assert result[0]["id"] == "test-scheme"

    saved = json.loads(
        cache_file.read_text(
            encoding="utf-8"
        )
    )

    assert saved["count"] == 1

    assert (
        saved["schemes"][0]["source"]["authority"]
        == "Government Test Authority"
    )