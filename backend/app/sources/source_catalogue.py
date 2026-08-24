from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


SourceType = Literal[
    "html_listing",
    "data_gov",
    "json_api",
    "csv",
    "directory",
]


@dataclass(frozen=True)
class GovernmentSourceConfig:
    source_id: str
    name: str
    source_type: SourceType

    authority: str

    base_url: str
    listing_url: str | None = None

    allowed_domains: tuple[str, ...] = ()
    allowed_path_prefixes: tuple[str, ...] = ()

    # We only automatically crawl a source when
    # we have deliberately approved it.
    automated_access_allowed: bool = False

    enabled: bool = True


GOVERNMENT_SOURCES: list[GovernmentSourceConfig] = [
    GovernmentSourceConfig(
        source_id="data-gov-in",
        name="Open Government Data Platform India",
        source_type="data_gov",
        authority=(
            "National Informatics Centre, "
            "Ministry of Electronics & Information Technology, "
            "Government of India"
        ),
        base_url="https://data.gov.in",
        allowed_domains=(
            "data.gov.in",
            "api.data.gov.in",
        ),
        automated_access_allowed=True,
    ),

    GovernmentSourceConfig(
        source_id="india-gov-directory",
        name="National Portal of India - Government Web Directory",
        source_type="directory",
        authority=(
            "National Informatics Centre, "
            "Ministry of Electronics & Information Technology, "
            "Government of India"
        ),
        base_url="https://www.india.gov.in",
        listing_url=(
            "https://www.india.gov.in/"
            "directory/web-directory"
        ),
        allowed_domains=(
            "www.india.gov.in",
            "india.gov.in",
        ),

        # We are using this as a trusted directory
        # reference first, not blindly crawling it.
        automated_access_allowed=False,
    ),
]