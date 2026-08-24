from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class SchemeValidationResult:
    valid: bool
    reason: str


class SchemeValidationService:
    """
    Validates whether a discovered government page is
    good enough to be stored as a real scheme record.

    Main rule:
    A page must come from a trusted government domain
    AND contain usable extracted scheme information.
    """

    BLOCKED_PATH_KEYWORDS = {
        "help",
        "contact",
        "about",
        "privacy",
        "disclaimer",
        "feedback",
        "sitemap",
        "site-map",
        "site_map",
        "tender",
        "recruitment",
        "vacancy",
        "gallery",
        "news",
        "press",
        "login",
        "signin",
        "sign-in",
        "screenreader",
        "screen-reader",
        "directory",
        "minister",
        "ministers",
        "history",
        "publication",
        "statistics",
        "report",
        "annual",
        "budget",
        "parliament",
        "download",
        "archive",
        "magazine",
        "conference",
        "circular",
        "weather",
        "result",
    }

    SCHEME_SIGNALS = {
        "eligibility",
        "eligible",
        "beneficiary",
        "beneficiaries",
        "benefit",
        "benefits",
        "financial assistance",
        "financial support",
        "how to apply",
        "application",
        "application process",
        "documents required",
        "scheme",
        "yojana",
        "programme",
        "program",
        "mission",
        "subsidy",
        "scholarship",
        "pension",
        "insurance",
        "guidelines",
        "assistance",
        "support",
    }

    STRONG_IDENTITY_SIGNALS = {
        "scheme",
        "schemes",
        "yojana",
        "programme",
        "program",
        "mission",
        "subsidy",
        "scholarship",
        "pension",
        "insurance",
    }

    def validate(
        self,
        scheme: dict,
    ) -> SchemeValidationResult:
        source = (
            scheme.get("source", {})
            or {}
        )

        scheme_id = str(
            scheme.get(
                "id",
                "",
            )
        ).strip()

        name = str(
            scheme.get(
                "name",
                "",
            )
        ).strip()

        url = str(
            source.get(
                "url",
                "",
            )
        ).strip()

        official_text = str(
            scheme.get(
                "official_text",
                "",
            )
        ).strip()

        # -------------------------------------------------
        # Required basic fields
        # -------------------------------------------------

        if not scheme_id:
            return SchemeValidationResult(
                False,
                "Missing scheme id.",
            )

        if not name:
            return SchemeValidationResult(
                False,
                "Missing scheme name.",
            )

        if not url:
            return SchemeValidationResult(
                False,
                "Missing official source URL.",
            )

        # -------------------------------------------------
        # URL validation
        # -------------------------------------------------

        parsed = urlparse(url)

        if parsed.scheme != "https":
            return SchemeValidationResult(
                False,
                "Official source must use HTTPS.",
            )

        domain = (
            parsed.netloc
            .lower()
            .strip()
        )

        if not self._is_trusted_government_domain(
            domain
        ):
            return SchemeValidationResult(
                False,
                "Source is not a trusted government domain.",
            )

        path = (
            parsed.path
            .lower()
            .strip()
        )

        if any(
            keyword in path
            for keyword
            in self.BLOCKED_PATH_KEYWORDS
        ):
            return SchemeValidationResult(
                False,
                "Page looks like navigation/admin content.",
            )

        # -------------------------------------------------
        # Official page must contain actual content
        # -------------------------------------------------

        if len(official_text) < 120:
            return SchemeValidationResult(
                False,
                "Official content is too short.",
            )

        # -------------------------------------------------
        # Determine whether page looks scheme-related
        # -------------------------------------------------

        benefits = str(
            scheme.get(
                "benefits",
                "",
            )
            or ""
        ).strip()

        application_process = str(
            scheme.get(
                "application_process",
                "",
            )
            or ""
        ).strip()

        eligibility = scheme.get(
            "eligibility",
            {},
        )

        eligibility_summary = ""

        if isinstance(
            eligibility,
            dict,
        ):
            eligibility_summary = str(
                eligibility.get(
                    "summary",
                    "",
                )
                or ""
            ).strip()

        documents = scheme.get(
            "documents",
            [],
        )

        searchable = " ".join(
            [
                name,
                path,
                official_text,
                benefits,
                application_process,
                eligibility_summary,
            ]
        ).lower()

        matched_signals = {
            signal
            for signal
            in self.SCHEME_SIGNALS
            if signal in searchable
        }

        strong_scheme_identity = any(
            signal
            in f"{name} {path}".lower()
            for signal
            in self.STRONG_IDENTITY_SIGNALS
        )

        # -------------------------------------------------
        # Count actual extracted useful fields
        # -------------------------------------------------

        meaningful_sections = 0

        if benefits:
            meaningful_sections += 1

        if application_process:
            meaningful_sections += 1

        if eligibility_summary:
            meaningful_sections += 1

        if documents:
            meaningful_sections += 1

        # This is the important safety gate.
        # We do NOT store a page merely because its URL
        # contains "scheme".
        if meaningful_sections < 1:
            return SchemeValidationResult(
                False,
                "No usable scheme details were extracted.",
            )

        # -------------------------------------------------
        # Require sufficient scheme evidence
        # -------------------------------------------------

        if len(matched_signals) < 2:
            return SchemeValidationResult(
                False,
                "Not enough scheme-specific signals.",
            )

        if not strong_scheme_identity:
            # Some valid pages may not literally include
            # "scheme" in the URL, so structured extraction
            # can still save them if evidence is strong.
            if meaningful_sections < 2:
                return SchemeValidationResult(
                    False,
                    "Page identity is too weak for a scheme record.",
                )

        # -------------------------------------------------
        # Final acceptance
        # -------------------------------------------------

        return SchemeValidationResult(
            True,
            "Validated using trusted source and extracted scheme details.",
        )

    @staticmethod
    def _is_trusted_government_domain(
        domain: str,
    ) -> bool:
        domain = (
            domain
            .lower()
            .strip()
        )

        return (
            domain == "gov.in"
            or domain.endswith(
                ".gov.in"
            )
            or domain == "nic.in"
            or domain.endswith(
                ".nic.in"
            )
        )


scheme_validation_service = (
    SchemeValidationService()
)