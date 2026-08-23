from __future__ import annotations

import re
from typing import Any


class OfficialContentExtractionService:
    """
    Extract common scheme sections from normalized
    official-government page text.

    Important:
    Only strong/clear section headings are recognised.
    We intentionally avoid broad aliases such as
    'assistance' or 'apply' because those words can
    occur naturally inside scheme descriptions.
    """

    SECTION_ALIASES = {
        "eligibility": {
            "eligibility",
            "eligibility criteria",
            "who can apply",
            "who is eligible",
            "eligible beneficiaries",
            "beneficiary eligibility",
        },

        "benefits": {
            "benefits",
            "scheme benefits",
            "benefits of the scheme",
            "key benefits",
        },

        "application_process": {
            "how to apply",
            "application process",
            "application procedure",
            "application process and procedure",
            "how to apply for the scheme",
        },

        "documents": {
            "documents required",
            "required documents",
            "documents needed",
            "documents required for application",
        },
    }

    def extract(
        self,
        text: str,
    ) -> dict[str, Any]:
        cleaned_text = self._clean_text(text)

        if not cleaned_text:
            return self._empty_result()

        sections = self._split_into_sections(
            cleaned_text
        )

        return {
            "eligibility": sections.get(
                "eligibility",
                "",
            ).strip(),

            "benefits": sections.get(
                "benefits",
                "",
            ).strip(),

            "application_process": sections.get(
                "application_process",
                "",
            ).strip(),

            "documents": sections.get(
                "documents",
                "",
            ).strip(),
        }

    @staticmethod
    def _clean_text(
        text: str,
    ) -> str:
        value = str(text or "")

        value = value.replace(
            "\r\n",
            "\n",
        )

        value = value.replace(
            "\r",
            "\n",
        )

        # Remove extra horizontal whitespace,
        # but preserve newlines because headings
        # generally appear on separate lines.
        value = re.sub(
            r"[ \t]+",
            " ",
            value,
        )

        value = re.sub(
            r"\n[ \t]+",
            "\n",
            value,
        )

        value = re.sub(
            r"\n{3,}",
            "\n\n",
            value,
        )

        return value.strip()

    def _split_into_sections(
        self,
        text: str,
    ) -> dict[str, str]:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        collected: dict[str, list[str]] = {
            "eligibility": [],
            "benefits": [],
            "application_process": [],
            "documents": [],
        }

        current_section: str | None = None

        for line in lines:
            section = self._identify_heading(
                line
            )

            if section is not None:
                current_section = section
                continue

            if current_section is not None:
                collected[current_section].append(
                    line
                )

        return {
            section: self._join_content(lines)
            for section, lines
            in collected.items()
        }

    def _identify_heading(
        self,
        line: str,
    ) -> str | None:
        """
        Returns a known section only when the entire
        line looks like a strong section heading.

        This avoids confusing content such as:

            "financial assistance"

        with the Benefits heading.
        """

        normalized = self._normalize_heading(
            line
        )

        if not normalized:
            return None

        # Real section headings should be reasonably
        # short. This also prevents full sentences
        # from being classified as headings.
        if len(normalized) > 60:
            return None

        for section, aliases in (
            self.SECTION_ALIASES.items()
        ):
            if normalized in aliases:
                return section

        return None

    @staticmethod
    def _normalize_heading(
        value: str,
    ) -> str:
        value = str(value).lower().strip()

        # Remove common heading punctuation.
        value = re.sub(
            r"[:\-–—]+$",
            "",
            value,
        )

        value = re.sub(
            r"[^a-z0-9 ]",
            "",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    @staticmethod
    def _join_content(
        lines: list[str],
    ) -> str:
        if not lines:
            return ""

        text = " ".join(lines)

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    @staticmethod
    def _empty_result() -> dict[str, str]:
        return {
            "eligibility": "",
            "benefits": "",
            "application_process": "",
            "documents": "",
        }


official_content_extractor = (
    OfficialContentExtractionService()
)