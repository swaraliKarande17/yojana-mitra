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

def test_extracts_benefit_from_normal_prose():
    service = OfficialContentExtractionService()

    text = """
    Plastic Park Scheme.

    The scheme supports development of Plastic Parks
    for the plastics processing industry.

    Government of India provides grant funding up to
    50% of the project cost, subject to a ceiling of
    Rs. 40 crore per project.
    """

    result = service.extract(text)

    assert "grant funding" in result["benefits"].lower()
    assert "50%" in result["benefits"]


def test_extracts_multiple_fields_from_normal_prose():
    service = OfficialContentExtractionService()

    text = """
    Farmer Support Scheme.

    Small and marginal farmers are eligible for the scheme.

    The scheme provides financial assistance of
    Rs. 6,000 per year.

    Eligible farmers may apply through the official
    government portal.

    Applicants must submit Aadhaar and bank account details.
    """

    result = service.extract(text)

    assert "eligible" in result["eligibility"].lower()
    assert "financial assistance" in result["benefits"].lower()
    assert "apply through" in result["application_process"].lower()
    assert "aadhaar" in result["documents"].lower()

def test_preserves_rupee_abbreviation_and_full_benefit():
    service = OfficialContentExtractionService()

    text = """
    Plastic Park Scheme

    Government of India provides grant funding up to
    50% of the project cost, subject to a ceiling of
    Rs. 40 crore per project.
    """

    result = service.extract(text)

    assert (
        "Government of India"
        in result["benefits"]
    )

    assert (
        "50%"
        in result["benefits"]
    )

    assert (
        "Rs. 40 crore"
        in result["benefits"]
    )