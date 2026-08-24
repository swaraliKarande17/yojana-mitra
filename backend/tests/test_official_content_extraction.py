from app.services.official_content_extraction_service import (
    OfficialContentExtractionService,
)


def test_extracts_inline_sections():
    service = OfficialContentExtractionService()

    text = """
    Farmer Support Scheme

    Eligibility: Eligible farmers with valid land records may apply.

    Benefits: Financial assistance is provided to eligible farmers.

    How to Apply: Applications can be submitted through the official portal.

    Documents Required: Aadhaar Card and bank account details.
    """

    result = service.extract(text)

    assert "Eligible farmers" in result["eligibility"]
    assert "Financial assistance" in result["benefits"]
    assert "official portal" in result["application_process"]
    assert "Aadhaar Card" in result["documents"]