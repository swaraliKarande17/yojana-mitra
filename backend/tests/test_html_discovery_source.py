from app.sources.html_discovery_source import (
    HTMLDiscoverySource,
)


def make_discovery_source():
    return HTMLDiscoverySource(
        listing_url=(
            "https://schemes.example.gov.in/"
            "schemes"
        ),
        allowed_domains={
            "schemes.example.gov.in"
        },
        allowed_path_prefixes=(
            "/scheme/",
        ),
    )


def test_discovers_scheme_links():
    source = make_discovery_source()

    html = """
    <html>
        <body>
            <a href="/scheme/farmer-support">
                Farmer Support Scheme
            </a>

            <a href="/scheme/student-scholarship">
                Student Scholarship Scheme
            </a>

            <a href="/about">
                About Portal
            </a>

            <a href="https://evil.example.com/scheme/fake">
                Fake Scheme
            </a>
        </body>
    </html>
    """

    links = source.extract_links(html)

    assert len(links) == 2

    urls = {
        item.url
        for item in links
    }

    assert (
        "https://schemes.example.gov.in/"
        "scheme/farmer-support"
        in urls
    )

    assert (
        "https://schemes.example.gov.in/"
        "scheme/student-scholarship"
        in urls
    )


def test_deduplicates_links():
    source = make_discovery_source()

    html = """
    <a href="/scheme/test">
        Test Scheme
    </a>

    <a href="/scheme/test">
        Test Scheme Again
    </a>
    """

    links = source.extract_links(html)

    assert len(links) == 1


def test_rejects_external_domains():
    source = make_discovery_source()

    html = """
    <a href="https://random-site.com/scheme/test">
        Random Site
    </a>
    """

    links = source.extract_links(html)

    assert links == []