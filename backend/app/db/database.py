from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "yojana_mitra.db"
)


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DB_PATH,
        timeout=10,
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON;"
    )

    connection.execute(
        "PRAGMA journal_mode = WAL;"
    )

    return connection


def initialize_database() -> None:
    with get_connection() as connection:

        # -------------------------
        # Schemes
        # -------------------------

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schemes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                short_name TEXT,

                level TEXT,
                state TEXT,
                ministry TEXT,

                category_json TEXT NOT NULL DEFAULT '[]',
                target_groups_json TEXT NOT NULL DEFAULT '[]',

                eligibility_json TEXT NOT NULL DEFAULT '{}',
                benefits TEXT,
                documents_json TEXT NOT NULL DEFAULT '[]',
                application_process TEXT,

                keywords_json TEXT NOT NULL DEFAULT '[]',

                official_scheme_url TEXT NOT NULL,
                application_url TEXT,

                source_authority TEXT NOT NULL,
                source_domain TEXT,
                source_type TEXT,

                official_text TEXT,

                fetched_at TEXT NOT NULL,
                verified_at TEXT,

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_schemes_name
            ON schemes(name);
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_schemes_state
            ON schemes(state);
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_schemes_ministry
            ON schemes(ministry);
            """
        )

        # -------------------------
        # Government portals
        # -------------------------

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS government_portals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                domain TEXT NOT NULL,
                category TEXT,

                source_name TEXT,
                source_url TEXT,

                discovered_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,

                is_active INTEGER NOT NULL DEFAULT 1
            );
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_government_portals_domain
            ON government_portals(domain);
            """
        )