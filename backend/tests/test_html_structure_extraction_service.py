from app.services.html_structure_extraction_service import (
    HTMLStructureExtractionService,
)


def test_extracts_scheme_fields_from_table():
    service = HTMLStructureExtractionService()

    html = """
    <table>
        <tr>
            <th>Eligibility</th>
            <td>
                Small and marginal farmers may apply.
            </td>
        </tr>

        <tr>
            <th>Benefits</th>
            <td>
                Financial assistance of Rs. 6,000 per year.
            </td>
        </tr>

        <tr>
            <th>How to Apply</th>
            <td>
                Apply through the official portal.
            </td>
        </tr>

        <tr>
            <th>Documents Required</th>
            <td>
                Aadhaar Card and bank details.
            </td>
        </tr>
    </table>
    """

    result = service.extract(html)

    assert "farmers" in result["eligibility"].lower()
    assert "6,000" in result["benefits"]
    assert "official portal" in result["application_process"]
    assert "Aadhaar" in result["documents"]


def test_extracts_definition_list():
    service = HTMLStructureExtractionService()

    html = """
    <dl>
        <dt>Eligibility</dt>
        <dd>Women above 18 years may apply.</dd>

        <dt>Benefits</dt>
        <dd>Financial support is provided.</dd>
    </dl>
    """

    result = service.extract(html)

    assert "Women above 18" in result["eligibility"]
    assert "Financial support" in result["benefits"]


def test_extracts_labelled_card():
    service = HTMLStructureExtractionService()

    html = """
    <div class="scheme-card">
        <h3>Eligibility</h3>
        <p>
            Applicants must be residents of India.
        </p>
    </div>

    <div class="scheme-card">
        <h3>Benefits</h3>
        <p>
            Eligible applicants receive financial assistance.
        </p>
    </div>
    """

    result = service.extract(html)

    assert "residents of India" in result["eligibility"]
    assert "financial assistance" in result["benefits"]