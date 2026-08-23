from __future__ import annotations

import json
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


def _to_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
    )


def _from_json(
    value: str | None,
    default: Any,
) -> Any:
    if not value:
        return default

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


class SchemeStore:
    def __init__(self) -> None:
        initialize_database()

    def upsert(
        self,
        scheme: dict[str, Any],
    ) -> None:
        self._validate_scheme(scheme)

        source = scheme.get(
            "source",
            {},
        )

        now = _utc_now()

        official_url = (
            source.get("url")
            or scheme.get(
                "official_scheme_url"
            )
        )

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO schemes (
                    id,
                    name,
                    short_name,

                    level,
                    state,
                    ministry,

                    category_json,
                    target_groups_json,

                    eligibility_json,
                    benefits,
                    documents_json,
                    application_process,

                    keywords_json,

                    official_scheme_url,
                    application_url,

                    source_authority,
                    source_domain,
                    source_type,

                    official_text,

                    fetched_at,
                    verified_at,

                    created_at,
                    updated_at
                )
                VALUES (
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?, ?, ?, ?,
                    ?,
                    ?, ?,
                    ?, ?, ?,
                    ?,
                    ?, ?,
                    ?, ?
                )
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    short_name = excluded.short_name,

                    level = excluded.level,
                    state = excluded.state,
                    ministry = excluded.ministry,

                    category_json = excluded.category_json,
                    target_groups_json = excluded.target_groups_json,

                    eligibility_json = excluded.eligibility_json,
                    benefits = excluded.benefits,
                    documents_json = excluded.documents_json,
                    application_process = excluded.application_process,

                    keywords_json = excluded.keywords_json,

                    official_scheme_url = excluded.official_scheme_url,
                    application_url = excluded.application_url,

                    source_authority = excluded.source_authority,
                    source_domain = excluded.source_domain,
                    source_type = excluded.source_type,

                    official_text = excluded.official_text,

                    fetched_at = excluded.fetched_at,
                    verified_at = excluded.verified_at,

                    updated_at = excluded.updated_at;
                """,
                (
                    scheme["id"],
                    scheme["name"],
                    scheme.get("short_name"),

                    scheme.get("level"),
                    scheme.get("state"),
                    scheme.get("ministry"),

                    _to_json(
                        scheme.get(
                            "category",
                            [],
                        )
                    ),

                    _to_json(
                        scheme.get(
                            "target_groups",
                            [],
                        )
                    ),

                    _to_json(
                        scheme.get(
                            "eligibility",
                            {},
                        )
                    ),

                    scheme.get("benefits"),

                    _to_json(
                        scheme.get(
                            "documents",
                            [],
                        )
                    ),

                    scheme.get(
                        "application_process"
                    ),

                    _to_json(
                        scheme.get(
                            "keywords",
                            [],
                        )
                    ),

                    official_url,

                    scheme.get(
                        "application_url"
                    )
                    or source.get(
                        "application_url"
                    ),

                    source.get(
                        "authority"
                    ),

                    source.get(
                        "domain"
                    ),

                    source.get(
                        "source_type"
                    ),

                    scheme.get(
                        "official_text"
                    ),

                    source.get(
                        "fetched_at"
                    )
                    or now,

                    source.get(
                        "verified_at"
                    ),

                    now,
                    now,
                ),
            )

    def upsert_many(
        self,
        schemes: list[dict[str, Any]],
    ) -> None:
        for scheme in schemes:
            self.upsert(scheme)

    def get_all(
        self,
    ) -> list[dict[str, Any]]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM schemes
                ORDER BY name ASC;
                """
            ).fetchall()

        return [
            self._row_to_scheme(row)
            for row in rows
        ]

    def get_by_id(
        self,
        scheme_id: str,
    ) -> dict[str, Any] | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM schemes
                WHERE id = ?;
                """,
                (
                    scheme_id.strip(),
                ),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_scheme(row)

    def count(
        self,
    ) -> int:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM schemes;
                """
            ).fetchone()

        return int(row["count"])

    @staticmethod
    def _validate_scheme(
        scheme: dict[str, Any],
    ) -> None:
        if not scheme.get("id"):
            raise ValueError(
                "Scheme id is required."
            )

        if not scheme.get("name"):
            raise ValueError(
                "Scheme name is required."
            )

        source = scheme.get(
            "source",
            {},
        )

        if not source.get("authority"):
            raise ValueError(
                "Source authority is required."
            )

        if not (
            source.get("url")
            or scheme.get(
                "official_scheme_url"
            )
        ):
            raise ValueError(
                "Official source URL is required."
            )

    @staticmethod
    def _row_to_scheme(
        row,
    ) -> dict[str, Any]:
        return {
            "id": row["id"],
            "name": row["name"],
            "short_name": row["short_name"],

            "level": row["level"],
            "state": row["state"],
            "ministry": row["ministry"],

            "category": _from_json(
                row["category_json"],
                [],
            ),

            "target_groups": _from_json(
                row["target_groups_json"],
                [],
            ),

            "eligibility": _from_json(
                row["eligibility_json"],
                {},
            ),

            "benefits": row["benefits"],

            "documents": _from_json(
                row["documents_json"],
                [],
            ),

            "application_process": (
                row["application_process"]
            ),

            "keywords": _from_json(
                row["keywords_json"],
                [],
            ),

            "official_scheme_url": (
                row["official_scheme_url"]
            ),

            "application_url": (
                row["application_url"]
            ),

            "official_text": (
                row["official_text"]
            ),

            "source": {
                "authority": (
                    row["source_authority"]
                ),
                "domain": (
                    row["source_domain"]
                ),
                "source_type": (
                    row["source_type"]
                ),
                "url": (
                    row["official_scheme_url"]
                ),
                "fetched_at": (
                    row["fetched_at"]
                ),
                "verified_at": (
                    row["verified_at"]
                ),
            },
        }


scheme_store = SchemeStore()