from app.services.source_catalogue_service import (
    SourceCatalogueService,
)


def test_catalogue_contains_sources():
    service = SourceCatalogueService()

    sources = service.get_enabled_sources()

    assert len(sources) >= 2


def test_only_approved_sources_are_automatic():
    service = SourceCatalogueService()

    automatic_sources = (
        service.get_approved_automatic_sources()
    )

    assert all(
        source.automated_access_allowed
        for source in automatic_sources
    )