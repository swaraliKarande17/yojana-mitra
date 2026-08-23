from app.services.official_content_extraction_service import (
    OfficialContentExtractionService,
)


def test_extracts_official_sections():
    service = OfficialContentExtractionService()

    text = """
    Pradhan Mantri Example Scheme

    Eligibility
    Applicant must be an Indian citizen.
    Applicant must be at least 18 years old.

    Benefits
    Eligible applicants receive financial support.

    How to Apply
    Applications can be submitted through the official portal.

    Documents Required
    Aadhaar Card
    Bank account details
    """

    result = service.extract(text)

    assert "Indian citizen" in result["eligibility"]
    assert "financial support" in result["benefits"]
    assert "official portal" in result["application_process"]
    assert "Aadhaar Card" in result["documents"]