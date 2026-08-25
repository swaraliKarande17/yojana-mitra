import pytest

import app.db.database as database_module

from app.db.scheme_store import SchemeStore
from app.services.discovery_ingestion_service import (
    DiscoveryIngestionService,
)
from app.sources.html_discovery_source import (
    DiscoveredSchemeLink,
)


class FakeDiscoverySource:
    async def discover(self):
        return [
            DiscoveredSchemeLink(
                name="Farmer Support Scheme",
                url=(
                    "https://example.gov.in/"
                    "scheme/farmer-support"
                ),
                source_domain="example.gov.in",
            )
        ]


async def fake_fetch_schemes(self):
    return [
        self.normalize(
            {
                "html": """
                <html>
                    <body>
                        <h1>
                            Farmer Support Scheme
                        </h1>

                        <p>
                            Farmer Support Scheme is a government
                            programme created to provide financial
                            and agricultural assistance to eligible
                            farmers.
                        </p>

                        <h2>Eligibility</h2>
                        <p>
                            Small and marginal farmers with valid
                            agricultural land records may apply
                            under the scheme.
                        </p>

                        <h2>Benefits</h2>
                        <p>
                            Eligible farmers receive financial
                            assistance and support for agricultural
                            development activities.
                        </p>

                        <h2>How to Apply</h2>
                        <p>
                            Applications can be submitted through
                            the official government portal after
                            completing the required registration.
                        </p>

                        <h2>Documents Required</h2>
                        <p>
                            Aadhaar Card, bank account details,
                            identity proof and valid land records
                            are required.
                        </p>
                    </body>
                </html>
                """
            }
        )
    ]


@pytest.mark.asyncio
async def test_discovery_ingestion_to_sqlite(
    tmp_path,
    monkeypatch,
):
    test_db = (
        tmp_path
        / "discovery.db"
    )

    monkeypatch.setattr(
        database_module,
        "DB_PATH",
        test_db,
    )

    from app.sources import html_scheme_source

    monkeypatch.setattr(
        html_scheme_source.HTMLSchemeSource,
        "fetch_schemes",
        fake_fetch_schemes,
    )

    store = SchemeStore()

    service = DiscoveryIngestionService(
        store=store,
        concurrency=2,
    )

    result = await service.ingest_source(
        discovery_source=FakeDiscoverySource(),
        authority="Government Test Department",
        category=[
            "Agriculture"
        ],
        target_groups=[
            "Farmer"
        ],
        keywords=[
            "farmer",
            "support",
        ],
    )

    assert result.discovered == 1
    assert result.ingested == 1
    assert result.failed == 0

    assert store.count() == 1

    saved = store.get_by_id(
        "farmer-support"
    )

    assert saved is not None

    assert (
        saved["name"]
        == "Farmer Support Scheme"
    )

    assert (
        "farmer"
        in saved["eligibility"][
            "summary"
        ].lower()
    )

    assert (
            "financial assistance"
            in saved["benefits"].lower()
    )

    assert (
            "agricultural development"
            in saved["benefits"].lower()
    )