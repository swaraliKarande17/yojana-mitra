from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class DiscoveredSchemeLink:
    name: str
    url: str
    source_domain: str


class HTMLDiscoverySource:
    """
    Generic discovery adapter for permitted official
    government scheme listing/index pages.

    It discovers candidate scheme links but does not
    fetch or normalize scheme details.
    """

    def __init__(
        self,
        *,
        listing_url: str,
        allowed_domains: set[str],
        allowed_path_prefixes: tuple[str, ...] = (),
        timeout_seconds: float = 20.0,
    ) -> None:
        self.listing_url = listing_url.strip()

        self.allowed_domains = {
            domain.lower().strip()
            for domain in allowed_domains
            if domain.strip()
        }

        self.allowed_path_prefixes = (
            allowed_path_prefixes
        )

        self.timeout_seconds = timeout_seconds

        self._validate_config()

    def _validate_config(self) -> None:
        parsed = urlparse(
            self.listing_url
        )

        if parsed.scheme != "https":
            raise ValueError(
                "Discovery source must use HTTPS."
            )

        if not parsed.netloc:
            raise ValueError(
                "Invalid discovery URL."
            )

        if (
            parsed.netloc.lower()
            not in self.allowed_domains
        ):
            raise ValueError(
                "Listing domain is not trusted."
            )

    async def discover(
        self,
    ) -> list[DiscoveredSchemeLink]:
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
                    "Government Scheme Discovery"
                )
            },
        ) as client:
            response = await client.get(
                self.listing_url
            )

            response.raise_for_status()

        return self.extract_links(
            response.text
        )

    def extract_links(
        self,
        html: str,
    ) -> list[DiscoveredSchemeLink]:
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        discovered: dict[
            str,
            DiscoveredSchemeLink
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
                self.listing_url,
                href,
            )

            if not self._is_allowed_url(
                absolute_url
            ):
                continue

            discovered.setdefault(
                absolute_url,
                DiscoveredSchemeLink(
                    name=name,
                    url=absolute_url,
                    source_domain=urlparse(
                        absolute_url
                    ).netloc.lower(),
                ),
            )

        return list(
            discovered.values()
        )

    def _is_allowed_url(
        self,
        url: str,
    ) -> bool:
        parsed = urlparse(url)

        if parsed.scheme != "https":
            return False

        if (
            parsed.netloc.lower()
            not in self.allowed_domains
        ):
            return False

        if not self.allowed_path_prefixes:
            return True

        return any(
            parsed.path.startswith(prefix)
            for prefix
            in self.allowed_path_prefixes
        )