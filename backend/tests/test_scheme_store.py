from pathlib import Path

import app.db.database as database_module
from app.db.scheme_store import SchemeStore


def test_scheme_store_upsert_and_read(
    tmp_path,
    monkeypatch,
):
    test_db = (
        tmp_path
        / "test_yojana_mitra.db"
    )

    monkeypatch.setattr(
        database_module,
        "DB_PATH",
        test_db,
    )

    store = SchemeStore()

    scheme = {
        "id": "test-scheme",
        "name": "Test Government Scheme",
        "short_name": "TEST",

        "level": "Central",
        "state": "All India",
        "ministry": "Test Ministry",

        "category": [
            "Testing",
        ],

        "target_groups": [
            "Citizen",
        ],

        "eligibility": {
            "summary": (
                "Eligible citizens."
            )
        },

        "benefits": (
            "Financial assistance."
        ),

        "documents": [
            "Aadhaar Card",
        ],

        "application_process": (
            "Apply online."
        ),

        "keywords": [
            "test",
        ],

        "official_text": (
            "Official government text."
        ),

        "source": {
            "authority": (
                "Government Test Department"
            ),
            "domain": (
                "example.gov.in"
            ),
            "source_type": "html",
            "url": (
                "https://example.gov.in/"
                "scheme/test"
            ),
            "fetched_at": (
                "2026-08-23T00:00:00+00:00"
            ),
        },
    }

    store.upsert(scheme)

    assert store.count() == 1

    saved = store.get_by_id(
        "test-scheme"
    )

    assert saved is not None

    assert (
        saved["name"]
        == "Test Government Scheme"
    )

    assert (
        saved["eligibility"]["summary"]
        == "Eligible citizens."
    )

    assert (
        saved["source"]["authority"]
        == "Government Test Department"
    )


def test_scheme_store_updates_existing_scheme(
    tmp_path,
    monkeypatch,
):
    test_db = (
        tmp_path
        / "test_update.db"
    )

    monkeypatch.setattr(
        database_module,
        "DB_PATH",
        test_db,
    )

    store = SchemeStore()

    base_scheme = {
        "id": "scheme-1",
        "name": "Old Name",

        "category": [],
        "target_groups": [],
        "eligibility": {},
        "documents": [],
        "keywords": [],

        "source": {
            "authority": "Government",
            "url": (
                "https://example.gov.in/"
                "scheme"
            ),
            "fetched_at": (
                "2026-08-23T00:00:00+00:00"
            ),
        },
    }

    store.upsert(
        base_scheme
    )

    updated = {
        **base_scheme,
        "name": "New Name",
        "benefits": "Updated benefits",
    }

    store.upsert(
        updated
    )

    assert store.count() == 1

    saved = store.get_by_id(
        "scheme-1"
    )

    assert saved["name"] == "New Name"

    assert (
        saved["benefits"]
        == "Updated benefits"
    )