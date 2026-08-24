import asyncio

from app.db.portal_store import portal_store
from app.db.scheme_store import scheme_store
from app.services.portal_scheme_ingestion_service import (
    portal_scheme_ingestion_service,
)


async def main():
    print(
        "\n=== Yojana Mitra Portal Scheme Ingestion ==="
    )

    print(
        f"Stored portals before run: "
        f"{portal_store.count()}"
    )

    print(
        f"Stored schemes before run: "
        f"{scheme_store.count()}"
    )

    result = (
        await portal_scheme_ingestion_service
        .run()
    )

    print("\n=== Result ===")

    print(
        f"Portals checked: "
        f"{result.portals_checked}"
    )

    print(
        f"Listing pages found: "
        f"{result.listing_pages_found}"
    )

    print(
        f"Scheme links discovered: "
        f"{result.schemes_discovered}"
    )

    print(
        f"Schemes ingested: "
        f"{result.schemes_ingested}"
    )

    print(
        f"Failures: "
        f"{result.failed}"
    )

    print(
        f"Stored schemes after run: "
        f"{scheme_store.count()}"
    )


if __name__ == "__main__":
    asyncio.run(main())