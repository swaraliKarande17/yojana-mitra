from app.config import settings
from app.sources.data_gov_source import DataGovSource


def get_official_sources():
    return [
        DataGovSource(
            resource_id="388208c6-d82a-4190-90df-91aa2c326fec",
            api_key=settings.data_gov_api_key,
            scheme_id="pm-kisan",
            scheme_name="PM-KISAN",
            official_source_url=(
                "https://data.gov.in/catalog/"
                "pm-kisan-scheme"
            ),
            category=["Agriculture"],
            target_groups=["Farmer"],
            keywords=[
                "farmer",
                "pm kisan",
                "agriculture",
                "income support",
            ],
            base_url=settings.data_gov_base_url,
            timeout_seconds=settings.data_gov_timeout_seconds,
            limit=1,
        ),
    ]