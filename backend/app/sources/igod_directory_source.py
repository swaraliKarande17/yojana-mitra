from __future__ import annotations

import asyncio
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class IGODPortal:
    name: str
    url: str
    domain: str
    category: str


class IGODDirectorySource:
    """
    Discover real government websites through IGOD.

    Correct flow:

    IGOD listing
        -> IGOD organization detail page
        -> external official Website URL

    IGOD navigation/category pages are never returned
    as government portals.
    """

    BASE_URL = "https://igod.gov.in"

    DIRECTORY_PAGES = {
        "union_ministries": (
            "https://igod.gov.in/ug/E002/organizations"
        ),
        "union_departments": (
            "https://igod.gov.in/ug/E003/organizations"
        ),
    }

    def __init__(
        self,
        timeout_seconds: float = 20.0,
        concurrency: int = 5,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.concurrency = max(
            1,
            min(concurrency, 10),
        )

    async def discover_all(
        self,
    ) -> list[IGODPortal]:
        detail_pages: dict[str, str] = {}

        async with self._client() as client:
            for category, listing_url in (
                self.DIRECTORY_PAGES.items()
            ):
                try:
                    response = await client.get(
                        listing_url
                    )

                    response.raise_for_status()

                    links = (
                        self.extract_organization_links(
                            html=response.text,
                            listing_url=listing_url,
                        )
                    )

                    for url in links:
                        detail_pages.setdefault(
                            url,
                            category,
                        )

                except httpx.RequestError as exc:
                    print(
                        "[IGOD] Listing request failed "
                        f"for {category}: {exc}"
                    )

                except httpx.HTTPStatusError as exc:
                    print(
                        "[IGOD] Listing HTTP error "
                        f"{exc.response.status_code} "
                        f"for {category}"
                    )

        if not detail_pages:
            return []

        semaphore = asyncio.Semaphore(
            self.concurrency
        )

        async def process_detail(
            detail_url: str,
            category: str,
        ) -> IGODPortal | None:
            async with semaphore:
                try:
                    async with self._client() as client:
                        response = await client.get(
                            detail_url
                        )

                        response.raise_for_status()

                    return self.extract_official_portal(
                        html=response.text,
                        category=category,
                    )

                except httpx.RequestError as exc:
                    print(
                        "[IGOD] Detail request failed: "
                        f"{detail_url}: {exc}"
                    )

                except httpx.HTTPStatusError as exc:
                    print(
                        "[IGOD] Detail HTTP error "
                        f"{exc.response.status_code}: "
                        f"{detail_url}"
                    )

                return None

        results = await asyncio.gather(
            *[
                process_detail(
                    detail_url,
                    category,
                )
                for detail_url, category
                in detail_pages.items()
            ]
        )

        portals: dict[str, IGODPortal] = {}

        for portal in results:
            if portal is None:
                continue

            portals.setdefault(
                portal.domain,
                portal,
            )

        return list(
            portals.values()
        )

    def extract_organization_links(
        self,
        *,
        html: str,
        listing_url: str,
    ) -> list[str]:
        """
        Return only IGOD organization-detail URLs.

        Example:
        https://igod.gov.in/organization/abc123
        """

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        results: set[str] = set()

        for anchor in soup.find_all(
            "a",
            href=True,
        ):
            href = anchor.get(
                "href",
                "",
            ).strip()

            absolute_url = urljoin(
                listing_url,
                href,
            )

            parsed = urlparse(
                absolute_url
            )

            if (
                parsed.netloc.lower()
                != "igod.gov.in"
            ):
                continue

            if not parsed.path.startswith(
                "/organization/"
            ):
                continue

            results.add(
                absolute_url
            )

        return sorted(results)

    def extract_official_portal(
        self,
        *,
        html: str,
        category: str,
    ) -> IGODPortal | None:
        """
        Read one IGOD organization page and extract
        the external official government Website URL.
        """

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        heading = soup.find(
            ["h1", "h2"]
        )

        name = (
            heading.get_text(
                " ",
                strip=True,
            )
            if heading
            else "Government Organization"
        )

        for anchor in soup.find_all(
            "a",
            href=True,
        ):
            href = anchor.get(
                "href",
                "",
            ).strip()

            parsed = urlparse(href)

            if parsed.scheme != "https":
                continue

            domain = (
                parsed.netloc
                .lower()
                .strip()
            )

            # Never store IGOD itself as the
            # discovered government portal.
            if (
                domain == "igod.gov.in"
                or domain.endswith(
                    ".igod.gov.in"
                )
            ):
                continue

            if not self._is_government_domain(
                domain
            ):
                continue

            return IGODPortal(
                name=name,
                url=href,
                domain=domain,
                category=category,
            )

        return None

    def _client(
        self,
    ) -> httpx.AsyncClient:
        timeout = httpx.Timeout(
            connect=10.0,
            read=self.timeout_seconds,
            write=10.0,
            pool=10.0,
        )

        return httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Yojana-Mitra/1.0 "
                    "Government Portal Discovery"
                )
            },
        )

    @staticmethod
    def _is_government_domain(
        domain: str,
    ) -> bool:
        domain = domain.lower()

        return (
            domain.endswith(".gov.in")
            or domain == "gov.in"
            or domain.endswith(".nic.in")
            or domain == "nic.in"
        )