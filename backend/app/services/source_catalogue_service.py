from app.sources.source_catalogue import (
    GOVERNMENT_SOURCES,
    GovernmentSourceConfig,
)


class SourceCatalogueService:
    def get_enabled_sources(
        self,
    ) -> list[GovernmentSourceConfig]:
        return [
            source
            for source in GOVERNMENT_SOURCES
            if source.enabled
        ]

    def get_approved_automatic_sources(
        self,
    ) -> list[GovernmentSourceConfig]:
        return [
            source
            for source in GOVERNMENT_SOURCES
            if (
                source.enabled
                and source.automated_access_allowed
            )
        ]

    def get_by_id(
        self,
        source_id: str,
    ) -> GovernmentSourceConfig | None:
        for source in GOVERNMENT_SOURCES:
            if source.source_id == source_id:
                return source

        return None


source_catalogue_service = SourceCatalogueService()