from app.sources.igod_directory_source import (
    IGODDirectorySource,
)


def test_extracts_only_organization_detail_links():
    source = IGODDirectorySource()

    html = """
    <html>
        <body>
            <a href="/organization/abc123">
                Details
            </a>

            <a href="/sg/MH/categories">
                Maharashtra
            </a>

            <a href="/help">
                Help
            </a>
        </body>
    </html>
    """

    links = source.extract_organization_links(
        html=html,
        listing_url=(
            "https://igod.gov.in/"
            "ug/E002/organizations"
        ),
    )

    assert links == [
        "https://igod.gov.in/"
        "organization/abc123"
    ]


def test_extracts_real_external_gov_portal():
    source = IGODDirectorySource()

    html = """
    <html>
        <body>

            <h2>
                Ministry of Agriculture
            </h2>

            <a href="https://agriculture.gov.in">
                Website
            </a>

            <a href="https://igod.gov.in/help">
                Help
            </a>

        </body>
    </html>
    """

    portal = source.extract_official_portal(
        html=html,
        category="union_ministries",
    )

    assert portal is not None

    assert (
        portal.domain
        == "agriculture.gov.in"
    )

    assert (
        portal.url
        == "https://agriculture.gov.in"
    )


def test_does_not_return_igod_as_portal():
    source = IGODDirectorySource()

    html = """
    <a href="https://igod.gov.in/help">
        Help
    </a>
    """

    portal = source.extract_official_portal(
        html=html,
        category="test",
    )

    assert portal is None