from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.db.scheme_store import scheme_store


class SchemeRepository:
    """
    Central read layer for Yojana Mitra.

    Priority:
    1. SQLite official scheme store
    2. Official JSON cache
    3. Legacy schemes.json fallback
    """

    def __init__(self) -> None:
        data_dir = (
            Path(__file__).resolve().parent.parent
            / "data"
        )

        self.official_cache_path = (
            data_dir
            / "official_scheme_cache.json"
        )

        self.fallback_path = (
            data_dir
            / "schemes.json"
        )

    @staticmethod
    def _read_json(
        path: Path,
    ) -> Any:
        if not path.exists():
            return None

        try:
            return json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

        except (
            json.JSONDecodeError,
            OSError,
        ):
            return None

    def _load_from_sqlite(
        self,
    ) -> list[dict]:
        try:
            schemes = scheme_store.get_all()

            if not isinstance(
                schemes,
                list,
            ):
                return []

            return [
                self._ensure_legacy_fields(
                    scheme
                )
                for scheme in schemes
            ]

        except Exception as exc:
            print(
                "[SCHEME REPOSITORY] "
                f"SQLite unavailable: {exc}"
            )

            return []

    def _load_official_cache(
        self,
    ) -> list[dict]:
        payload = self._read_json(
            self.official_cache_path
        )

        if not isinstance(
            payload,
            dict,
        ):
            return []

        schemes = payload.get(
            "schemes",
            [],
        )

        if not isinstance(
            schemes,
            list,
        ):
            return []

        return [
            self._ensure_legacy_fields(
                scheme
            )
            for scheme in schemes
        ]

    def _load_fallback(
        self,
    ) -> list[dict]:
        payload = self._read_json(
            self.fallback_path
        )

        if not isinstance(
            payload,
            list,
        ):
            return []

        return [
            self._ensure_legacy_fields(
                scheme
            )
            for scheme in payload
        ]

    def load_all(
        self,
    ) -> list[dict]:
        sqlite_schemes = (
            self._load_from_sqlite()
        )

        if sqlite_schemes:
            return sqlite_schemes

        official_schemes = (
            self._load_official_cache()
        )

        if official_schemes:
            return official_schemes

        return self._load_fallback()

    def get_all(
        self,
    ) -> list[dict]:
        return self.load_all()

    def get_by_id(
        self,
        scheme_id: str,
    ) -> dict | None:
        normalized_id = (
            scheme_id
            .strip()
            .lower()
        )

        for scheme in self.load_all():
            current_id = str(
                scheme.get(
                    "id",
                    "",
                )
            ).lower()

            if current_id == normalized_id:
                return scheme

        return None

    @staticmethod
    def _ensure_legacy_fields(
        scheme: dict,
    ) -> dict:
        """
        Keep compatibility with retrieval/chat code
        while storage is being migrated to SQLite.
        """

        result = dict(scheme)

        source = result.get(
            "source",
            {},
        )

        if not isinstance(
            source,
            dict,
        ):
            source = {}

        if not result.get(
            "official_source"
        ):
            result["official_source"] = (
                result.get(
                    "official_scheme_url"
                )
                or source.get("url")
                or ""
            )

        result.setdefault(
            "category",
            [],
        )

        result.setdefault(
            "target_groups",
            [],
        )

        result.setdefault(
            "eligibility",
            {},
        )

        result.setdefault(
            "benefits",
            "",
        )

        result.setdefault(
            "documents",
            [],
        )

        result.setdefault(
            "application_process",
            "",
        )

        result.setdefault(
            "keywords",
            [],
        )

        return result


scheme_repository = SchemeRepository()