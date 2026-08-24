from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.database import (
    get_connection,
    initialize_database,
)


def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


class PortalStore:
    def __init__(self) -> None:
        initialize_database()

    def upsert(
        self,
        portal: dict[str, Any],
    ) -> None:
        self._validate(portal)

        now = _utc_now()

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO government_portals (
                    name,
                    url,
                    domain,
                    category,
                    source_name,
                    source_url,
                    discovered_at,
                    last_seen_at,
                    is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)

                ON CONFLICT(url) DO UPDATE SET
                    name = excluded.name,
                    domain = excluded.domain,
                    category = excluded.category,
                    source_name = excluded.source_name,
                    source_url = excluded.source_url,
                    last_seen_at = excluded.last_seen_at,
                    is_active = 1;
                """,
                (
                    portal["name"],
                    portal["url"],
                    portal["domain"],
                    portal.get("category"),
                    portal.get("source_name"),
                    portal.get("source_url"),
                    now,
                    now,
                ),
            )

    def upsert_many(
        self,
        portals: list[dict[str, Any]],
    ) -> None:
        for portal in portals:
            self.upsert(portal)

    def get_all(
        self,
        *,
        active_only: bool = True,
    ) -> list[dict]:
        query = """
            SELECT *
            FROM government_portals
        """

        if active_only:
            query += " WHERE is_active = 1"

        query += " ORDER BY name ASC"

        with get_connection() as connection:
            rows = connection.execute(
                query
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def count(
        self,
    ) -> int:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM government_portals
                WHERE is_active = 1;
                """
            ).fetchone()

        return int(row["count"])

    @staticmethod
    def _validate(
        portal: dict[str, Any],
    ) -> None:
        for field in (
            "name",
            "url",
            "domain",
        ):
            if not portal.get(field):
                raise ValueError(
                    f"{field} is required."
                )


portal_store = PortalStore()