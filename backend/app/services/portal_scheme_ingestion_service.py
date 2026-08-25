from __future__ import annotations

from dataclasses import dataclass

from app.db.portal_store import portal_store
from app.db.scheme_store import scheme_store
from app.services.discovery_ingestion_service import (
    DiscoveryIngestionService,
)
from app.services.scheme_listing_discovery_service import (
    SchemeListingDiscoveryService,
)
from app.sources.html_discovery_source import (
    HTMLDiscoverySource,
)


@dataclass(frozen=True)
class PortalSchemeIngestionSummary:
    portals_checked: int
    listing_pages_found: int
    schemes_discovered: int
    schemes_ingested: int
    failed: int


class PortalSchemeIngestionService:
    """
    End-to-end portal ingestion:

    stored government portal
        -> likely scheme listing pages
        -> individual scheme links
        -> scheme detail extraction
        -> SQLite
    """

    def __init__(
        self,
        *,
        max_portals: int = 20,
        listing_limit_per_portal: int = 5,
        concurrency: int = 4,
    ) -> None:
        self.max_portals = max(1, max_portals)
        self.listing_limit_per_portal = max(
            1,
            listing_limit_per_portal,
        )

        self.listing_discovery = (
            SchemeListingDiscoveryService(
                max_results=self.listing_limit_per_portal
            )
        )

        self.scheme_ingestion = (
            DiscoveryIngestionService(
                store=scheme_store,
                concurrency=concurrency,
            )
        )

    async def run(
        self,
    ) -> PortalSchemeIngestionSummary:
        portals = portal_store.get_all()[
            : self.max_portals
        ]

        portals_checked = 0
        listing_pages_found = 0
        schemes_discovered = 0
        schemes_ingested = 0
        failed = 0

        for portal in portals:
            portals_checked += 1

            try:
                listing_pages = (
                    await self.listing_discovery.discover(
                        portal_url=portal["url"],
                        trusted_domain=portal["domain"],
                    )
                )

            except Exception as exc:
                failed += 1

                print(
                    "[PORTAL INGESTION] "
                    f"Listing discovery failed for "
                    f"{portal['url']}: {exc}"
                )

                continue

            listing_pages_found += len(
                listing_pages
            )

            for listing_page in listing_pages:
                try:
                    discovery_source = (
                        HTMLDiscoverySource(
                            listing_url=(
                                listing_page.url
                            ),
                            allowed_domains={
                                portal["domain"]
                            },
                            timeout_seconds=20.0,
                            # Controlled development run.
                            # Prevent one badly structured portal
                            # from producing hundreds of requests.
                            max_results=20,
                        )
                    )

                    result = (
                        await self.scheme_ingestion
                        .ingest_source(
                            discovery_source=(
                                discovery_source
                            ),
                            authority=(
                                portal.get("name")
                                or portal["domain"]
                            ),
                        )
                    )

                    schemes_discovered += (
                        result.discovered
                    )

                    schemes_ingested += (
                        result.ingested
                    )

                    failed += (
                        result.failed
                    )

                except Exception as exc:
                    failed += 1

                    print(
                        "[PORTAL INGESTION] "
                        f"Scheme ingestion failed for "
                        f"{listing_page.url}: {exc}"
                    )

        return PortalSchemeIngestionSummary(
            portals_checked=portals_checked,
            listing_pages_found=(
                listing_pages_found
            ),
            schemes_discovered=(
                schemes_discovered
            ),
            schemes_ingested=(
                schemes_ingested
            ),
            failed=failed,
        )


portal_scheme_ingestion_service = (
    PortalSchemeIngestionService()
)