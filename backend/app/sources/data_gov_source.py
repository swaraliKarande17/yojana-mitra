from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.sources.base_source import GovernmentSource


class DataGovSource(GovernmentSource):
    source_name = "Open Government Data Platform India"
    authority = (
        "National Informatics Centre, "
        "Ministry of Electronics & Information Technology, "
        "Government of India"
    )

    def __init__(
        self,
        *,
        resource_id: str,
        api_key: str,
        scheme_id: str,
        scheme_name: str,
        official_source_url: str,
        category: list[str] | None = None,
        target_groups: list[str] | None = None,
        keywords: list[str] | None = None,
        base_url: str = "https://api.data.gov.in/resource",
        timeout_seconds: float = 15.0,
        limit: int = 100,
    ) -> None:
        self.resource_id = resource_id.strip()
        self.api_key = api_key.strip()
        self.scheme_id = scheme_id.strip()
        self.scheme_name = scheme_name.strip()
        self.official_source_url = official_source_url.strip()

        self.category = category or []
        self.target_groups = target_groups or []
        self.keywords = keywords or []

        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.limit = limit

        if not self.resource_id:
            raise ValueError("resource_id is required.")

        if not self.scheme_id:
            raise ValueError("scheme_id is required.")

        if not self.scheme_name:
            raise ValueError("scheme_name is required.")

        if not self.official_source_url:
            raise ValueError(
                "official_source_url is required."
            )

    async def fetch_schemes(
        self,
    ) -> list[dict[str, Any]]:
        url = f"{self.base_url}/{self.resource_id}"

        params: dict[str, Any] = {
            "format": "json",
            "offset": 0,
            "limit": self.limit,
        }

        if self.api_key:
            params["api-key"] = self.api_key

        async with httpx.AsyncClient(
            timeout=self.timeout_seconds
        ) as client:
            response = await client.get(
                url,
                params=params,
            )

            response.raise_for_status()

            payload = response.json()

        raw_records = payload.get("records", [])

        if not isinstance(raw_records, list):
            raise ValueError(
                "data.gov.in returned invalid records."
            )

        return [
            self.normalize(
                {
                    "records": raw_records,
                    "total": payload.get("total"),
                }
            )
        ]

    def normalize(
        self,
        raw_item: dict[str, Any],
    ) -> dict[str, Any]:
        records = raw_item.get("records", [])

        return {
            "id": self.scheme_id,
            "name": self.scheme_name,
            "short_name": self.scheme_name,
            "category": self.category,
            "target_groups": self.target_groups,
            "eligibility": {},
            "benefits": "",
            "application_process": "",
            "keywords": self.keywords,
            "official_data": {
                "record_count": len(records),
                "records": records,
            },
            "source": {
                "authority": self.authority,
                "source_name": self.source_name,
                "url": self.official_source_url,
                "resource_id": self.resource_id,
                "fetched_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            },
        }