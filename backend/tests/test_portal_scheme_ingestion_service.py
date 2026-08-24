import pytest

import app.db.database as database_module

from app.db.portal_store import PortalStore
from app.db.scheme_store import SchemeStore
from app.services.portal_scheme_ingestion_service import (
    PortalSchemeIngestionService,
)


@pytest.mark.asyncio
async def test_empty_portal_store_is_safe(
    tmp_path,
    monkeypatch,
):
    test_db = (
        tmp_path
        / "portal_pipeline.db"
    )

    monkeypatch.setattr(
        database_module,
        "DB_PATH",
        test_db,
    )

    portal_store = PortalStore()
    scheme_store = SchemeStore()

    service = PortalSchemeIngestionService()

    # Replace module-level stores used by service.
    import app.services.portal_scheme_ingestion_service as module

    monkeypatch.setattr(
        module,
        "portal_store",
        portal_store,
    )

    monkeypatch.setattr(
        module,
        "scheme_store",
        scheme_store,
    )

    result = await service.run()

    assert result.portals_checked == 0
    assert result.listing_pages_found == 0
    assert result.schemes_discovered == 0
    assert result.schemes_ingested == 0
    assert result.failed == 0