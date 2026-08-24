import pytest

import app.db.database as database_module


@pytest.fixture(autouse=True)
def isolate_sqlite_database(tmp_path, monkeypatch):
    """
    Every test gets its own temporary SQLite database.

    Tests must never depend on or modify the real
    development database.
    """

    test_db = tmp_path / "yojana_mitra_test.db"

    monkeypatch.setattr(
        database_module,
        "DB_PATH",
        test_db,
    )

    yield