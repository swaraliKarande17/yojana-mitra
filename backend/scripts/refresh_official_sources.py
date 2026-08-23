import asyncio
from pathlib import Path

from app.services.source_ingestion_service import SourceIngestionService
from app.sources.registry import get_official_sources


CACHE_PATH = (
    Path(__file__).resolve().parent.parent
    / "app"
    / "data"
    / "official_scheme_cache.json"
)


async def main():
    sources = get_official_sources()

    service = SourceIngestionService(
        cache_path=CACHE_PATH
    )

    schemes = await service.ingest(
        sources
    )

    if not schemes:
        print(
            "No official sources were refreshed. "
            "Existing cache was preserved."
        )
        return

    print(
        f"Official cache refreshed successfully: "
        f"{len(schemes)} scheme(s)."
    )


if __name__ == "__main__":
    asyncio.run(main())