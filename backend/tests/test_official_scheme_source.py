from app.sources.official_scheme_source import (
    OfficialSchemeSource,
)


def test_official_scheme_source_normalization():
    source = OfficialSchemeSource(
        scheme_id="test-scheme",
        scheme_name="Test Scheme",
        source_url="https://example.gov.in/test",
        authority="Government Test Department",
        category=["Testing"],
        target_groups=["Citizen"],
        keywords=["test"],
    )

    result = source.normalize(
        {
            "html": """
                <html>
                    <body>
                        <h1>Test Scheme</h1>
                        <p>
                            This scheme provides support
                            to eligible citizens.
                        </p>
                    </body>
                </html>
            """
        }
    )

    assert result["id"] == "test-scheme"

    assert (
        "eligible citizens"
        in result["official_text"]
    )

    assert (
        result["source"]["authority"]
        == "Government Test Department"
    )