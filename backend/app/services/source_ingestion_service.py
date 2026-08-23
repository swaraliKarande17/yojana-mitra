import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from app.sources.base_source import GovernmentSource


class SourceIngestionService:
    def __init__(self, cache_path: Path) -> None:
        self.cache_path = cache_path

    async def ingest(
        self,
        sources: Iterable[GovernmentSource],
    ) -> list[dict]:
        collected_schemes: list[dict] = []

        for source in sources:
            try:
                schemes = await source.fetch_schemes()

                for scheme in schemes:
                    self._validate_scheme(scheme)
                    collected_schemes.append(scheme)

            except Exception as exc:
                print(
                    f"[SOURCE INGESTION] "
                    f"{source.source_name} failed: {exc}"
                )

        unique_schemes = self._deduplicate(collected_schemes)

        if unique_schemes:
            self._write_cache(unique_schemes)

        return unique_schemes

    @staticmethod
    def _validate_scheme(scheme: dict) -> None:
        required_fields = (
            "id",
            "name",
            "source",
        )

        missing = [
            field
            for field in required_fields
            if not scheme.get(field)
        ]

        if missing:
            raise ValueError(
                f"Invalid scheme record. Missing: {missing}"
            )

        source = scheme.get("source", {})

        if not source.get("url"):
            raise ValueError(
                f"Scheme {scheme.get('id')} has no official source URL."
            )

        if not source.get("authority"):
            raise ValueError(
                f"Scheme {scheme.get('id')} has no source authority."
            )

    @staticmethod
    def _deduplicate(
        schemes: list[dict],
    ) -> list[dict]:
        unique: dict[str, dict] = {}

        for scheme in schemes:
            scheme_id = scheme["id"]

            if scheme_id not in unique:
                unique[scheme_id] = scheme
                continue

            current = unique[scheme_id]

            current_time = (
                current
                .get("source", {})
                .get("fetched_at", "")
            )

            candidate_time = (
                scheme
                .get("source", {})
                .get("fetched_at", "")
            )

            if candidate_time > current_time:
                unique[scheme_id] = scheme

        return list(unique.values())

    def _write_cache(
        self,
        schemes: list[dict],
    ) -> None:
        self.cache_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "count": len(schemes),
            "schemes": schemes,
        }

        temporary_path = self.cache_path.with_suffix(
            ".tmp"
        )

        temporary_path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        temporary_path.replace(
            self.cache_path
        )