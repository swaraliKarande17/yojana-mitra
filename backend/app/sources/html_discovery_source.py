from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse, urldefrag

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

    It discovers only strong scheme/programme candidates.
    It does not fetch or normalize scheme details.
    """

    SCHEME_KEYWORDS = {
        "scheme",
        "schemes",
        "yojana",
        "programme",
        "programmes",
        "program",
        "programs",
        "mission",
        "subsidy",
        "assistance",
        "benefit",
        "benefits",
        "welfare",
        "scholarship",
        "pension",
        "insurance",
        "financial support",
        "financial assistance",
    }

    BLOCKED_KEYWORDS = {
        "about",
        "contact",
        "minister",
        "ministers",
        "directory",
        "history",
        "tender",
        "recruitment",
        "vacancy",
        "gallery",
        "video",
        "videos",
        "news",
        "press",
        "publication",
        "statistics",
        "statistical",
        "report",
        "reports",
        "annual",
        "budget",
        "parliament",
        "download",
        "downloads",
        "sitemap",
        "site_map",
        "screenreader",
        "screen-reader",
        "feedback",
        "disclaimer",
        "privacy",
        "login",
        "signin",
        "sign-in",
        "result",
        "results",
        "acts",
        "presentation",
        "weather",
        "archive",
        "archives",
        "magazine",
        "conference",
        "circular",
        "forms",
        "form",
    }

    BLOCKED_EXTENSIONS = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".zip",
        ".rar",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
    }

    def __init__(
        self,
        *,
        listing_url: str,
        allowed_domains: set[str],
        allowed_path_prefixes: tuple[str, ...] = (),
        timeout_seconds: float = 20.0,
        max_results: int = 25,
    ) -> None:
        self.listing_url = self._normalize_https_url(
            listing_url.strip()
        )

        self.allowed_domains = {
            domain.lower().strip()
            for domain in allowed_domains
            if domain.strip()
        }

        self.allowed_path_prefixes = allowed_path_prefixes

        self.timeout_seconds = timeout_seconds

        self.max_results = max(
            1,
            min(max_results, 100),
        )

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

        if not self._is_allowed_domain(
            parsed.netloc.lower()
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
                "",
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

            absolute_url = self._normalize_https_url(
                absolute_url
            )

            if not self._is_allowed_url(
                absolute_url
            ):
                continue

            if not self._is_scheme_candidate(
                url=absolute_url,
                text=name,
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

            if (
                len(discovered)
                >= self.max_results
            ):
                break

        return list(
            discovered.values()
        )

    def _is_scheme_candidate(
        self,
        *,
        url: str,
        text: str,
    ) -> bool:
        parsed = urlparse(url)

        path = parsed.path.lower()

        if any(
            path.endswith(extension)
            for extension in self.BLOCKED_EXTENSIONS
        ):
            return False

        searchable = (
            f"{text} {parsed.path}"
            .lower()
            .replace("_", " ")
            .replace("-", " ")
        )

        if any(
            keyword in searchable
            for keyword in self.BLOCKED_KEYWORDS
        ):
            return False

        return any(
            keyword in searchable
            for keyword in self.SCHEME_KEYWORDS
        )

    def _is_allowed_url(
        self,
        url: str,
    ) -> bool:
        parsed = urlparse(url)

        if parsed.scheme != "https":
            return False

        if not parsed.netloc:
            return False

        if not self._is_allowed_domain(
            parsed.netloc.lower()
        ):
            return False

        if not self.allowed_path_prefixes:
            return True

        return any(
            parsed.path.startswith(prefix)
            for prefix in self.allowed_path_prefixes
        )

    def _is_allowed_domain(
        self,
        candidate_domain: str,
    ) -> bool:
        candidate_domain = (
            candidate_domain
            .lower()
            .strip()
        )

        return any(
            candidate_domain == allowed
            or candidate_domain.endswith(
                f".{allowed}"
            )
            for allowed in self.allowed_domains
        )

    @staticmethod
    def _normalize_https_url(
            url: str,
    ) -> str:
        """
        Normalize discovered URLs so the same page is not
        processed multiple times.

        Examples:

        /schemes#top
        /schemes#content
        /schemes

        all become:

        /schemes
        """

        value = str(url or "").strip()

        if not value:
            return ""

        # Remove #fragment
        value, _ = urldefrag(value)

        parsed = urlparse(value)

        scheme = parsed.scheme.lower()

        if scheme == "http":
            scheme = "https"

        # Remove accidental duplicate slashes from path.
        path = parsed.path

        while "//" in path:
            path = path.replace("//", "/")

        # Keep root as "/".
        if path != "/":
            path = path.rstrip("/")

        normalized = parsed._replace(
            scheme=scheme,
            netloc=parsed.netloc.lower(),
            path=path,
            fragment="",
        )

        return normalized.geturl()