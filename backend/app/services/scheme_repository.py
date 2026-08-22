from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Any


class SchemeRepository:
    """Loads scheme data safely and reuses it until the file changes."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or Path(__file__).resolve().parents[1] / "data" / "schemes.json"
        self._lock = RLock()
        self._cached_mtime_ns: int | None = None
        self._cached_schemes: list[dict[str, Any]] = []

    def load_all(self) -> list[dict[str, Any]]:
        try:
            mtime_ns = self._path.stat().st_mtime_ns
        except OSError as exc:
            raise RuntimeError("Scheme data file is unavailable.") from exc

        with self._lock:
            if self._cached_mtime_ns == mtime_ns and self._cached_schemes:
                return [dict(item) for item in self._cached_schemes]

            try:
                payload = json.loads(self._path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise RuntimeError("Unable to load scheme data.") from exc

            if not isinstance(payload, list):
                raise RuntimeError("Scheme data must be a JSON array.")

            self._cached_schemes = payload
            self._cached_mtime_ns = mtime_ns
            return [dict(item) for item in payload]

    def get_by_id(self, scheme_id: str) -> dict[str, Any] | None:
        return next(
            (scheme for scheme in self.load_all() if scheme.get("id") == scheme_id),
            None,
        )


scheme_repository = SchemeRepository()