from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.services.html_structure_extraction_service import (
    html_structure_extractor,
)
from app.services.official_content_extraction_service import (
    official_content_extractor,
)
from app.sources.base_source import GovernmentSource


class HTMLSchemeSource(GovernmentSource):
    """
    Generic adapter for official government scheme webpages.
    """

    def __init__(
        self,
        *,
        scheme_id: str,
        scheme_name: str,
        source_url: str,
        authority: str,
        short_name: str | None = None,
        category: list[str] | None = None,
        target_groups: list[str] | None = None,
        keywords: list[str] | None = None,
        timeout_seconds: float = 20.0,
    ) -> None:
        self.scheme_id = scheme_id.strip()
        self.scheme_name = scheme_name.strip()

        self.short_name = (
            short_name.strip()
            if short_name
            else self.scheme_name
        )

        self.source_url = source_url.strip()
        self.authority = authority.strip()

        self.category = category or []
        self.target_groups = target_groups or []
        self.keywords = keywords or []

        self.timeout_seconds = timeout_seconds

        self._validate_configuration()

    def _validate_configuration(self) -> None:
        if not self.scheme_id:
            raise ValueError("scheme_id is required.")

        if not self.scheme_name:
            raise ValueError("scheme_name is required.")

        if not self.authority:
            raise ValueError("authority is required.")

        parsed = urlparse(self.source_url)

        if parsed.scheme != "https":
            raise ValueError(
                "Official source must use HTTPS."
            )

        if not parsed.netloc:
            raise ValueError(
                "Invalid official source URL."
            )

    @staticmethod
    def _extract_page_title(
        soup: BeautifulSoup,
        fallback: str,
    ) -> str:
        """
        Extract the actual scheme/page name.

        Priority:
        1. h1
        2. og:title
        3. title tag
        4. discovered-link fallback
        """

        h1 = soup.find("h1")

        if h1:
            value = h1.get_text(
                " ",
                strip=True,
            )

            if value:
                return value

        og_title = soup.find(
            "meta",
            attrs={
                "property": "og:title",
            },
        )

        if og_title:
            value = str(
                og_title.get(
                    "content",
                    "",
                )
            ).strip()

            if value:
                return value

        title_tag = soup.find("title")

        if title_tag:
            value = title_tag.get_text(
                " ",
                strip=True,
            )

            if value:
                for separator in (
                    " | ",
                    " :: ",
                ):
                    if separator in value:
                        value = value.split(
                            separator,
                            1,
                        )[0].strip()

                if value:
                    return value

        return fallback.strip()

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
                    "Official Government Scheme Indexer"
                )
            },
        ) as client:
            response = await client.get(
                self.source_url
            )

            response.raise_for_status()

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if (
            "text/html" not in content_type
            and "application/xhtml+xml"
            not in content_type
        ):
            raise ValueError(
                "Source did not return HTML."
            )

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
        html = str(
            raw_item.get(
                "html",
                "",
            )
        )

        # First extract structured data directly
        # from the original HTML.
        structured_html = (
            html_structure_extractor.extract(
                html
            )
        )

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        page_name = self._extract_page_title(
            soup,
            self.scheme_name,
        )

        # Remove non-content elements.
        for element in soup(
            [
                "script",
                "style",
                "noscript",
            ]
        ):
            element.decompose()

        official_text = soup.get_text(
            "\n",
            strip=True,
        )

        # Then extract information from flattened text.
        structured_text = (
            official_content_extractor.extract(
                official_text
            )
        )

        eligibility_text = (
            structured_html.get(
                "eligibility",
                "",
            ).strip()
            or structured_text.get(
                "eligibility",
                "",
            ).strip()
        )

        benefits_text = (
            structured_html.get(
                "benefits",
                "",
            ).strip()
            or structured_text.get(
                "benefits",
                "",
            ).strip()
        )

        application_text = (
            structured_html.get(
                "application_process",
                "",
            ).strip()
            or structured_text.get(
                "application_process",
                "",
            ).strip()
        )

        documents_text = (
            structured_html.get(
                "documents",
                "",
            ).strip()
            or structured_text.get(
                "documents",
                "",
            ).strip()
        )

        return {
            "id": self.scheme_id,

            "name": page_name,

            "short_name": (
                self.short_name
                if self.short_name != self.scheme_name
                else page_name
            ),

            "category": self.category,

            "target_groups": self.target_groups,

            "eligibility": {
                "summary": eligibility_text,
            },

            "benefits": benefits_text,

            "application_process": (
                application_text
            ),

            "documents": documents_text,

            "keywords": self.keywords,

            "official_text": official_text,

            "source": {
                "authority": self.authority,

                "source_type": "html",

                "url": self.source_url,

                "domain": urlparse(
                    self.source_url
                ).netloc.lower(),

                "fetched_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            },
        }