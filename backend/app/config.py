from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str
    host: str
    port: int
    allowed_origins: tuple[str, ...]
    gemini_api_key: str | None
    gemini_model: str
    gemini_timeout_seconds: float


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    origins = tuple(
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://127.0.0.1:5173,http://localhost:5173",
        ).split(",")
        if origin.strip()
    )

    return Settings(
        app_name="Yojana Mitra API",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5050")),
        allowed_origins=origins,
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
        gemini_timeout_seconds=float(os.getenv("GEMINI_TIMEOUT_SECONDS", "20")),
    )