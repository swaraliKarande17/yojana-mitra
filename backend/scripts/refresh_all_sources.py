import asyncio

from app.services.source_catalogue_ingestion_service import (
    source_catalogue_ingestion_service,
)


async def main():
    result = (
        await source_catalogue_ingestion_service
        .refresh_all()
    )

    print("\n=== Yojana Mitra Official Source Refresh ===")
    print(
        f"Configured sources: {result['sources']}"
    )
    print(
        f"Discovered schemes: {result['discovered']}"
    )
    print(
        f"Ingested schemes: {result['ingested']}"
    )
    print(
        f"Failed: {result['failed']}"
    )

    print("\nSource results:")

    for item in result["source_results"]:
        print(item)


if __name__ == "__main__":
    asyncio.run(main())