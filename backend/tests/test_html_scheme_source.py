import pytest

from app.sources.html_scheme_source import (
    HTMLSchemeSource,
)


def make_source():
    return HTMLSchemeSource(
        scheme_id="test-scheme",
        scheme_name="Test Government Scheme",
        short_name="TEST",
        source_url=(
            "https://example.gov.in/"
            "schemes/test"
        ),
        authority="Government Test Department",
        category=["Testing"],
        target_groups=["Citizen"],
        keywords=["test", "citizen"],
    )


def test_html_scheme_normalization():
    source = make_source()

    html = """
    <html>
        <body>
            <h1>Test Government Scheme</h1>

            <h2>Eligibility</h2>
            <p>
                Applicant must be an
                Indian citizen.
            </p>

            <h2>Benefits</h2>
            <p>
                Eligible applicants receive
                financial assistance.
            </p>

            <h2>How to Apply</h2>
            <p>
                Apply through the official
                government portal.
            </p>

            <h2>Documents Required</h2>
            <p>Aadhaar Card</p>

            <script>
                fake tracking information
            </script>
        </body>
    </html>
    """

    result = source.normalize(
        {
            "html": html,
        }
    )

    assert result["id"] == "test-scheme"
    assert result["short_name"] == "TEST"

    assert (
        "Indian citizen"
        in result["eligibility"]["summary"]
    )

    assert (
        "financial assistance"
        in result["benefits"]
    )

    assert (
        "official government portal"
        in result["application_process"]
    )

    assert (
        "Aadhaar Card"
        in result["documents"]
    )

    assert (
        "fake tracking information"
        not in result["official_text"]
    )

    assert (
        result["source"]["domain"]
        == "example.gov.in"
    )


def test_html_source_rejects_http():
    with pytest.raises(ValueError):
        HTMLSchemeSource(
            scheme_id="test",
            scheme_name="Test",
            source_url=(
                "http://example.gov.in/test"
            ),
            authority="Government",
        )


def test_html_source_rejects_invalid_url():
    with pytest.raises(ValueError):
        HTMLSchemeSource(
            scheme_id="test",
            scheme_name="Test",
            source_url="not-a-url",
            authority="Government",
        )