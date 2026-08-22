from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

MYSCHEME_BASE_URL = "https://www.myscheme.gov.in"
SLUG_RE = re.compile(r"^[a-z0-9-]+$")


class SchemeSourceError(RuntimeError):
    pass


async def fetch_scheme_page(scheme_slug: str) -> tuple[str, str]:
    if not isinstance(scheme_slug, str) or not scheme_slug.strip():
        raise ValueError("A valid scheme slug is required.")

    normalized_slug = scheme_slug.strip()
    if not SLUG_RE.fullmatch(normalized_slug):
        raise ValueError("Scheme slug contains invalid characters.")

    url = urljoin(MYSCHEME_BASE_URL, f"/schemes/{normalized_slug}")
    headers = {
        "User-Agent": "YojanaMitra/1.0",
        "Accept": "text/html,application/xhtml+xml",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0, headers=headers, follow_redirects=True) as client:
            response = await client.get(url)
            if response.status_code == 404:
                raise SchemeSourceError(f"Scheme not found: {normalized_slug}")
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise SchemeSourceError(f"Unable to fetch scheme from official source: {exc}") from exc

    return url, response.text


def extract_basic_scheme_data(html: str, source_url: str) -> dict[str, str | None]:
    if not isinstance(html, str) or not html.strip():
        raise ValueError("Valid HTML content is required.")

    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find("h1")
    title = heading.get_text(strip=True) if heading else None
    if not title and soup.title:
        title = soup.title.get_text(strip=True)

    description_tag = soup.find("meta", attrs={"name": "description"})
    description = description_tag.get("content", "").strip() if description_tag else None

    return {
        "name": title or None,
        "description": description or None,
        "sourceUrl": source_url,
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
    }


async def fetch_and_normalize_scheme(scheme_slug: str) -> dict[str, str | None]:
    url, html = await fetch_scheme_page(scheme_slug)
    return extract_basic_scheme_data(html, url)