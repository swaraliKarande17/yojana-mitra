from app.services.scheme_validation_service import (
    SchemeValidationService,
)


def make_valid_scheme():
    return {
        "id": "farmer-support",
        "name": "Farmer Support Scheme",

        "eligibility": {
            "summary": (
                "Eligible farmers may apply."
            )
        },

        "benefits": (
            "Financial assistance is provided "
            "to eligible farmers."
        ),

        "application_process": (
            "Apply through the official portal."
        ),

        "documents": [
            "Aadhaar Card"
        ],

        "official_text": (
            "Farmer Support Scheme. "
            "Eligibility: Eligible farmers may apply. "
            "Benefits include financial assistance. "
            "How to Apply: Apply through the official "
            "government portal. Documents Required: "
            "Aadhaar Card and bank details."
        ),

        "source": {
            "url": (
                "https://agriculture.gov.in/"
                "scheme/farmer-support"
            )
        },
    }


def test_accepts_valid_scheme():
    service = SchemeValidationService()

    result = service.validate(
        make_valid_scheme()
    )

    assert result.valid is True


def test_rejects_non_government_domain():
    service = SchemeValidationService()

    scheme = make_valid_scheme()

    scheme["source"]["url"] = (
        "https://random-company.com/scheme"
    )

    result = service.validate(
        scheme
    )

    assert result.valid is False


def test_rejects_help_page():
    service = SchemeValidationService()

    scheme = make_valid_scheme()

    scheme["source"]["url"] = (
        "https://agriculture.gov.in/help"
    )

    result = service.validate(
        scheme
    )

    assert result.valid is False


def test_rejects_empty_content():
    service = SchemeValidationService()

    scheme = make_valid_scheme()

    scheme["official_text"] = "Short text."

    result = service.validate(
        scheme
    )

    assert result.valid is False

def test_rejects_scheme_page_without_extracted_details():
    service = SchemeValidationService()

    scheme = {
        "id": "plastic-park-scheme",
        "name": "Plastic Park Scheme",

        "eligibility": {},
        "benefits": "",
        "documents": [],
        "application_process": "",

        "official_text": (
            "Plastic Park Scheme "
            "Government scheme guidelines for eligible "
            "applicants and beneficiaries. "
            "The programme provides financial assistance "
            "for development activities. "
        ) * 5,

        "source": {
            "url": (
                "https://chemicals.gov.in/"
                "plastic-park-scheme"
            )
        },
    }

    result = service.validate(
        scheme
    )

    assert result.valid is False

    assert (
        result.reason
        == "No usable scheme details were extracted."
    )

def test_rejects_generic_scheme_name():
    service = SchemeValidationService()

    scheme = make_valid_scheme()

    scheme["name"] = "English"

    result = service.validate(
        scheme
    )

    assert result.valid is False