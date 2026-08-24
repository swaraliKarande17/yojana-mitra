from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class GovernmentPortal:
    name: str
    url: str
    domain: str


class PortalDiscoveryService:
    """
    Discovers candidate official government portals
    from trusted government directory/index pages.

    This service does NOT crawl arbitrary websites.
    """

    def __init__(
        self,
        *,
        trusted_directory_url: str,
        allowed_directory_domains: set[str],
        timeout_seconds: float = 20.0,
    ) -> None:
        self.trusted_directory_url = (
            trusted_directory_url.strip()
        )

        self.allowed_directory_domains = {
            domain.lower().strip()
            for domain in allowed_directory_domains
            if domain.strip()
        }

        self.timeout_seconds = timeout_seconds

        self._validate_directory()

    def _validate_directory(self) -> None:
        parsed = urlparse(
            self.trusted_directory_url
        )

        if parsed.scheme != "https":
            raise ValueError(
                "Trusted directory must use HTTPS."
            )

        if (
            parsed.netloc.lower()
            not in self.allowed_directory_domains
        ):
            raise ValueError(
                "Directory domain is not trusted."
            )

    async def discover_portals(
        self,
    ) -> list[GovernmentPortal]:
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
                    "Government Portal Discovery"
                )
            },
        ) as client:
            response = await client.get(
                self.trusted_directory_url
            )

            response.raise_for_status()

        return self.extract_portals(
            response.text
        )

    def extract_portals(
        self,
        html: str,
    ) -> list[GovernmentPortal]:
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        portals: dict[
            str,
            GovernmentPortal
        ] = {}

        for anchor in soup.find_all(
            "a",
            href=True,
        ):
            href = anchor.get(
                "href",
                ""
            ).strip()

            name = anchor.get_text(
                " ",
                strip=True,
            )

            if not href or not name:
                continue

            absolute_url = urljoin(
                self.trusted_directory_url,
                href,
            )

            parsed = urlparse(
                absolute_url
            )

            if parsed.scheme != "https":
                continue

            domain = parsed.netloc.lower()

            if not self._looks_like_gov_domain(
                domain
            ):
                continue

            portals.setdefault(
                domain,
                GovernmentPortal(
                    name=name,
                    url=absolute_url,
                    domain=domain,
                ),
            )

        return list(
            portals.values()
        )

    @staticmethod
    def _looks_like_gov_domain(
        domain: str,
    ) -> bool:
        domain = domain.lower()

        return (
            domain.endswith(".gov.in")
            or domain == "gov.in"
            or domain.endswith(".nic.in")
            or domain == "nic.in"
        )