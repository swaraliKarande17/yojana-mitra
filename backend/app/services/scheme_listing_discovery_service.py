from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class SchemeListingPage:
    name: str
    url: str
    domain: str
    score: int


class SchemeListingDiscoveryService:
    """
    Finds likely scheme/programme listing pages
    inside a trusted government portal.

    It does NOT crawl external domains.
    """

    KEYWORDS = {
        "schemes": 10,
        "scheme": 9,
        "yojana": 9,
        "programmes": 8,
        "programme": 8,
        "programs": 8,
        "program": 8,
        "welfare": 7,
        "beneficiary": 6,
        "beneficiaries": 6,
        "initiatives": 5,
        "services": 4,
        "financial assistance": 4,
        "subsidy": 4,
        "scholarship": 4,
        "pension": 4,
    }

    IGNORE_KEYWORDS = {
        "login",
        "contact",
        "about",
        "privacy",
        "disclaimer",
        "feedback",
        "sitemap",
        "tender",
        "recruitment",
        "vacancy",
        "gallery",
        "news",
    }

    def __init__(
        self,
        *,
        timeout_seconds: float = 20.0,
        max_results: int = 20,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_results = max(
            1,
            min(max_results, 100),
        )

    async def discover(
        self,
        *,
        portal_url: str,
        trusted_domain: str,
    ) -> list[SchemeListingPage]:

        self._validate_portal(
            portal_url=portal_url,
            trusted_domain=trusted_domain,
        )

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
                    "Government Scheme Listing Discovery"
                )
            },
        ) as client:
            response = await client.get(
                portal_url
            )

            response.raise_for_status()

        return self.extract_listing_pages(
            html=response.text,
            portal_url=portal_url,
            trusted_domain=trusted_domain,
        )

    def extract_listing_pages(
        self,
        *,
        html: str,
        portal_url: str,
        trusted_domain: str,
    ) -> list[SchemeListingPage]:

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        discovered: dict[
            str,
            SchemeListingPage
        ] = {}

        trusted_domain = (
            trusted_domain
            .lower()
            .strip()
        )

        for anchor in soup.find_all(
            "a",
            href=True,
        ):
            href = anchor.get(
                "href",
                "",
            ).strip()

            name = anchor.get_text(
                " ",
                strip=True,
            )

            if not href:
                continue

            absolute_url = urljoin(
                portal_url,
                href,
            )

            parsed = urlparse(
                absolute_url
            )

            domain = (
                parsed.netloc
                .lower()
                .strip()
            )

            if not self._same_or_subdomain(
                domain,
                trusted_domain,
            ):
                continue

            score = self._score_candidate(
                name=name,
                url=absolute_url,
            )

            if score <= 0:
                continue

            current = discovered.get(
                absolute_url
            )

            candidate = SchemeListingPage(
                name=(
                    name
                    or parsed.path
                    or absolute_url
                ),
                url=absolute_url,
                domain=domain,
                score=score,
            )

            if (
                current is None
                or candidate.score
                > current.score
            ):
                discovered[
                    absolute_url
                ] = candidate

        results = sorted(
            discovered.values(),
            key=lambda item: (
                -item.score,
                item.url,
            ),
        )

        return results[
            : self.max_results
        ]

    def _score_candidate(
        self,
        *,
        name: str,
        url: str,
    ) -> int:

        searchable = (
            f"{name} {url}"
            .lower()
        )

        if any(
            ignored in searchable
            for ignored in self.IGNORE_KEYWORDS
        ):
            return 0

        score = 0

        for keyword, weight in (
            self.KEYWORDS.items()
        ):
            if keyword in searchable:
                score += weight

        parsed = urlparse(url)

        path = parsed.path.lower()

        # Stronger signal if URL itself
        # clearly looks like a scheme page.
        if "/scheme" in path:
            score += 8

        if "/yojana" in path:
            score += 8

        if "/programme" in path:
            score += 6

        if "/program" in path:
            score += 6

        if "/welfare" in path:
            score += 5

        return score

    @staticmethod
    def _same_or_subdomain(
        candidate_domain: str,
        trusted_domain: str,
    ) -> bool:

        return (
            candidate_domain
            == trusted_domain
            or candidate_domain.endswith(
                f".{trusted_domain}"
            )
        )

    @staticmethod
    def _validate_portal(
        *,
        portal_url: str,
        trusted_domain: str,
    ) -> None:

        parsed = urlparse(
            portal_url
        )

        if parsed.scheme != "https":
            raise ValueError(
                "Government portal must use HTTPS."
            )

        if not parsed.netloc:
            raise ValueError(
                "Invalid government portal URL."
            )

        actual_domain = (
            parsed.netloc
            .lower()
            .strip()
        )

        trusted_domain = (
            trusted_domain
            .lower()
            .strip()
        )

        if not (
            actual_domain
            == trusted_domain
            or actual_domain.endswith(
                f".{trusted_domain}"
            )
        ):
            raise ValueError(
                "Portal URL does not match "
                "the trusted domain."
            )


scheme_listing_discovery_service = (
    SchemeListingDiscoveryService()
)