from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx
from bs4 import BeautifulSoup

from app.sources.base_source import GovernmentSource

from app.services.official_content_extraction_service import (
    official_content_extractor,
)
class OfficialSchemeSource(GovernmentSource):
    source_name = "Official Government Scheme Page"

    def __init__(
        self,
        *,
        scheme_id: str,
        scheme_name: str,
        source_url: str,
        authority: str,
        category: list[str] | None = None,
        target_groups: list[str] | None = None,
        keywords: list[str] | None = None,
        timeout_seconds: float = 20.0,
    ) -> None:
        self.scheme_id = scheme_id.strip()
        self.scheme_name = scheme_name.strip()
        self.source_url = source_url.strip()
        self.authority = authority.strip()

        self.category = category or []
        self.target_groups = target_groups or []
        self.keywords = keywords or []
        self.timeout_seconds = timeout_seconds

        if not self.scheme_id:
            raise ValueError("scheme_id is required.")

        if not self.scheme_name:
            raise ValueError("scheme_name is required.")

        if not self.source_url:
            raise ValueError("source_url is required.")

        if not self.authority:
            raise ValueError("authority is required.")

    async def fetch_schemes(
        self,
    ) -> list[dict[str, Any]]:
        timeout = httpx.Timeout(
            connect=10.0,
            read=self.timeout_seconds,
            write=10.0,
            pool=10.0,
        )

        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Yojana-Mitra/1.0 "
                    "Government Scheme Verification"
                )
            },
        ) as client:
            response = await client.get(
                self.source_url
            )

            response.raise_for_status()

        return [
            self.normalize(
                {
                    "html": response.text,
                }
            )
        ]

    def normalize(
            self,
            raw_item: dict[str, Any],
    ) -> dict[str, Any]:

        html = raw_item.get("html", "")

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        text = soup.get_text(
            "\n",
            strip=True,
        )

        structured = official_content_extractor.extract(text)

        return {
            "id": self.scheme_id,
            "name": self.scheme_name,
            "short_name": self.scheme_name,
            "category": self.category,
            "target_groups": self.target_groups,

            "official_text": text,

            "eligibility": {
                "summary": structured["eligibility"]
            },

            "benefits": structured["benefits"],

            "application_process": structured[
                "application_process"
            ],

            "documents": structured["documents"],

            "keywords": self.keywords,

            "source": {
                "authority": self.authority,
                "source_name": self.source_name,
                "url": self.source_url,
                "fetched_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            },
        }