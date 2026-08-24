import pytest

from app.services.scheme_listing_discovery_service import (
    SchemeListingDiscoveryService,
)


def make_service():
    return SchemeListingDiscoveryService(
        max_results=10
    )


def test_discovers_scheme_listing_pages():
    service = make_service()

    html = """
    <html>
        <body>

            <a href="/schemes">
                Government Schemes
            </a>

            <a href="/welfare-programmes">
                Welfare Programmes
            </a>

            <a href="/yojana/farmers">
                Farmer Yojana
            </a>

            <a href="/about">
                About Us
            </a>

            <a href="/contact">
                Contact
            </a>

        </body>
    </html>
    """

    results = service.extract_listing_pages(
        html=html,
        portal_url=(
            "https://agriculture.gov.in"
        ),
        trusted_domain=(
            "agriculture.gov.in"
        ),
    )

    urls = {
        result.url
        for result in results
    }

    assert (
        "https://agriculture.gov.in/schemes"
        in urls
    )

    assert (
        "https://agriculture.gov.in/"
        "welfare-programmes"
        in urls
    )

    assert (
        "https://agriculture.gov.in/"
        "yojana/farmers"
        in urls
    )

    assert (
        "https://agriculture.gov.in/about"
        not in urls
    )


def test_rejects_external_domains():
    service = make_service()

    html = """
    <a href="https://random-company.com/schemes">
        Schemes
    </a>

    <a href="/schemes">
        Government Schemes
    </a>
    """

    results = service.extract_listing_pages(
        html=html,
        portal_url=(
            "https://health.gov.in"
        ),
        trusted_domain=(
            "health.gov.in"
        ),
    )

    assert len(results) == 1

    assert (
        results[0].domain
        == "health.gov.in"
    )


def test_allows_trusted_subdomain():
    service = make_service()

    html = """
    <a href="https://schemes.example.gov.in/schemes">
        Scheme Portal
    </a>
    """

    results = service.extract_listing_pages(
        html=html,
        portal_url=(
            "https://example.gov.in"
        ),
        trusted_domain=(
            "example.gov.in"
        ),
    )

    assert len(results) == 1

    assert (
        results[0].domain
        == "schemes.example.gov.in"
    )


@pytest.mark.asyncio
async def test_rejects_untrusted_portal():
    service = make_service()

    with pytest.raises(
        ValueError
    ):
        await service.discover(
            portal_url=(
                "https://evil-site.com"
            ),
            trusted_domain=(
                "gov.in"
            ),
        )