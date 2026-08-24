import app.db.database as database_module

from app.db.portal_store import PortalStore


def test_portal_store_upsert_and_read(
    tmp_path,
    monkeypatch,
):
    test_db = (
        tmp_path
        / "portal_store.db"
    )

    monkeypatch.setattr(
        database_module,
        "DB_PATH",
        test_db,
    )

    store = PortalStore()

    portal = {
        "name": "Ministry of Agriculture",
        "url": "https://agriculture.gov.in",
        "domain": "agriculture.gov.in",
        "category": "union_ministries",
        "source_name": "IGOD",
        "source_url": "https://igod.gov.in",
    }

    store.upsert(portal)

    assert store.count() == 1

    portals = store.get_all()

    assert len(portals) == 1
    assert (
        portals[0]["domain"]
        == "agriculture.gov.in"
    )


def test_portal_store_updates_existing(
    tmp_path,
    monkeypatch,
):
    test_db = (
        tmp_path
        / "portal_update.db"
    )

    monkeypatch.setattr(
        database_module,
        "DB_PATH",
        test_db,
    )

    store = PortalStore()

    portal = {
        "name": "Old Name",
        "url": "https://health.gov.in",
        "domain": "health.gov.in",
        "category": "union_ministries",
    }

    store.upsert(portal)

    updated = {
        **portal,
        "name": "Ministry of Health",
    }

    store.upsert(updated)

    assert store.count() == 1

    portals = store.get_all()

    assert (
        portals[0]["name"]
        == "Ministry of Health"
    )