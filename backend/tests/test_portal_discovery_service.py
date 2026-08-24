from app.services.portal_discovery_service import (
    PortalDiscoveryService,
)


def make_service():
    return PortalDiscoveryService(
        trusted_directory_url=(
            "https://directory.example.gov.in/"
            "government-portals"
        ),
        allowed_directory_domains={
            "directory.example.gov.in"
        },
    )


def test_discovers_government_portals():
    service = make_service()

    html = """
    <html>
        <body>
            <a href="https://agriculture.gov.in">
                Ministry of Agriculture
            </a>

            <a href="https://health.gov.in">
                Ministry of Health
            </a>

            <a href="https://education.nic.in">
                Education Portal
            </a>

            <a href="https://random-company.com">
                Random Company
            </a>
        </body>
    </html>
    """

    portals = service.extract_portals(
        html
    )

    domains = {
        portal.domain
        for portal in portals
    }

    assert "agriculture.gov.in" in domains
    assert "health.gov.in" in domains
    assert "education.nic.in" in domains

    assert "random-company.com" not in domains


def test_deduplicates_same_domain():
    service = make_service()

    html = """
    <a href="https://health.gov.in">
        Health
    </a>

    <a href="https://health.gov.in/schemes">
        Health Schemes
    </a>
    """

    portals = service.extract_portals(
        html
    )

    assert len(portals) == 1