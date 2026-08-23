from __future__ import annotations

import asyncio
import hashlib
import re
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlparse

from app.db.scheme_store import SchemeStore
from app.sources.html_discovery_source import (
    DiscoveredSchemeLink,
    HTMLDiscoverySource,
)
from app.sources.html_scheme_source import (
    HTMLSchemeSource,
)


@dataclass(frozen=True)
class DiscoveryIngestionResult:
    discovered: int
    ingested: int
    failed: int


class DiscoveryIngestionService:
    """
    Connects:

    listing discovery
        -> scheme detail fetching
        -> normalization
        -> SQLite storage
    """

    def __init__(
        self,
        *,
        store: SchemeStore,
        concurrency: int = 5,
    ) -> None:
        self.store = store
        self.concurrency = max(
            1,
            min(concurrency, 10),
        )

    async def ingest_source(
        self,
        *,
        discovery_source: HTMLDiscoverySource,
        authority: str,
        category: list[str] | None = None,
        target_groups: list[str] | None = None,
        keywords: list[str] | None = None,
    ) -> DiscoveryIngestionResult:
        links = await discovery_source.discover()

        if not links:
            return DiscoveryIngestionResult(
                discovered=0,
                ingested=0,
                failed=0,
            )

        semaphore = asyncio.Semaphore(
            self.concurrency
        )

        async def process_link(
            link: DiscoveredSchemeLink,
        ) -> bool:
            async with semaphore:
                try:
                    source = HTMLSchemeSource(
                        scheme_id=self._generate_scheme_id(
                            link
                        ),
                        scheme_name=link.name,
                        source_url=link.url,
                        authority=authority,
                        category=category,
                        target_groups=target_groups,
                        keywords=keywords,
                    )

                    schemes = (
                        await source.fetch_schemes()
                    )

                    if not schemes:
                        return False

                    for scheme in schemes:
                        self.store.upsert(
                            scheme
                        )

                    return True

                except Exception as exc:
                    print(
                        "[DISCOVERY INGESTION] "
                        f"Failed: {link.url} "
                        f"({type(exc).__name__}: {exc})"
                    )

                    return False

        results = await asyncio.gather(
            *[
                process_link(link)
                for link in links
            ]
        )

        ingested = sum(
            1
            for result in results
            if result
        )

        return DiscoveryIngestionResult(
            discovered=len(links),
            ingested=ingested,
            failed=len(links) - ingested,
        )

    @staticmethod
    def _generate_scheme_id(
        link: DiscoveredSchemeLink,
    ) -> str:
        """
        Generate a stable ID from the scheme URL.

        Example:
        https://portal.gov.in/scheme/farmer-support

        -> farmer-support

        Falls back to a short URL hash when necessary.
        """

        parsed = urlparse(
            link.url
        )

        path = parsed.path.strip("/")

        candidate = (
            path.split("/")[-1]
            if path
            else ""
        )

        candidate = candidate.lower()

        candidate = re.sub(
            r"[^a-z0-9-]+",
            "-",
            candidate,
        )

        candidate = candidate.strip("-")

        if candidate:
            return candidate

        digest = hashlib.sha256(
            link.url.encode(
                "utf-8"
            )
        ).hexdigest()[:16]

        return f"scheme-{digest}"