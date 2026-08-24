import asyncio

from app.db.portal_store import portal_store
from app.sources.igod_directory_source import (
    IGODDirectorySource,
)


def build_portal_record(portal):
    fallback_name = (
        portal.domain
        .replace("www.", "")
        .replace(".gov.in", "")
        .replace(".nic.in", "")
        .replace("-", " ")
        .replace("_", " ")
        .title()
    )

    name = (
        portal.name.strip()
        if portal.name and portal.name.strip()
        else fallback_name
    )

    if not name:
        return None

    if not portal.url:
        return None

    if not portal.domain:
        return None

    return {
        "name": name,
        "url": portal.url,
        "domain": portal.domain,
        "category": portal.category,
        "source_name": "IGOD",
        "source_url": "https://igod.gov.in",
    }


async def main():
    source = IGODDirectorySource(
        timeout_seconds=30.0,
        concurrency=5,
    )

    portals = await source.discover_all()

    print(
        "\n=== Yojana Mitra Government Portal Discovery ==="
    )

    print(
        f"Discovered candidates: {len(portals)}"
    )

    records = []

    for portal in portals:
        record = build_portal_record(
            portal
        )

        if record is None:
            print(
                "[PORTAL DISCOVERY] "
                f"Skipped invalid portal: {portal}"
            )
            continue

        records.append(record)

    if records:
        portal_store.upsert_many(
            records
        )

        print(
            f"Valid portals stored this run: "
            f"{len(records)}"
        )

    else:
        print(
            "No valid new government portals "
            "were discovered."
        )

    print(
        f"Stored active portals: "
        f"{portal_store.count()}"
    )

    print("\nStored portal sample:\n")

    for portal in portal_store.get_all()[:20]:
        print(
            f"{portal['name']} -> "
            f"{portal['url']}"
        )


if __name__ == "__main__":
    asyncio.run(main())