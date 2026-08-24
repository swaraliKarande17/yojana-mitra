from __future__ import annotations

from app.db.scheme_store import scheme_store
from app.services.discovery_ingestion_service import (
    DiscoveryIngestionService,
)
from app.services.source_catalogue_service import (
    source_catalogue_service,
)
from app.sources.html_discovery_source import (
    HTMLDiscoverySource,
)


class SourceCatalogueIngestionService:
    def __init__(self) -> None:
        self.discovery_ingestion = (
            DiscoveryIngestionService(
                store=scheme_store,
                concurrency=5,
            )
        )

    async def refresh_all(self) -> dict:
        sources = (
            source_catalogue_service
            .get_enabled_sources()
        )

        summary = {
            "sources": len(sources),
            "discovered": 0,
            "ingested": 0,
            "failed": 0,
            "source_results": [],
        }

        for source in sources:
            if source.source_type != "html_listing":
                continue

            try:
                discovery_source = HTMLDiscoverySource(
                    listing_url=source.listing_url,
                    allowed_domains=set(
                        source.allowed_domains
                    ),
                    allowed_path_prefixes=(
                        source.allowed_path_prefixes
                    ),
                )

                result = (
                    await self.discovery_ingestion
                    .ingest_source(
                        discovery_source=(
                            discovery_source
                        ),
                        authority=source.authority,
                    )
                )

                summary["discovered"] += (
                    result.discovered
                )

                summary["ingested"] += (
                    result.ingested
                )

                summary["failed"] += (
                    result.failed
                )

                summary[
                    "source_results"
                ].append(
                    {
                        "source_id": (
                            source.source_id
                        ),
                        "discovered": (
                            result.discovered
                        ),
                        "ingested": (
                            result.ingested
                        ),
                        "failed": (
                            result.failed
                        ),
                    }
                )

            except Exception as exc:
                summary["failed"] += 1

                summary[
                    "source_results"
                ].append(
                    {
                        "source_id": (
                            source.source_id
                        ),
                        "error": str(exc),
                    }
                )

        return summary


source_catalogue_ingestion_service = (
    SourceCatalogueIngestionService()
)