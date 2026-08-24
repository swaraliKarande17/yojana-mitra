from __future__ import annotations

import re
from typing import Any


class OfficialContentExtractionService:
    SECTION_ALIASES = {
        "eligibility": {
            "eligibility",
            "eligibility criteria",
            "who can apply",
            "who is eligible",
            "eligible beneficiaries",
            "beneficiary eligibility",
            "target beneficiaries",
        },

        "benefits": {
            "benefits",
            "scheme benefits",
            "benefits of the scheme",
            "key benefits",
            "financial benefits",
        },

        "application_process": {
            "how to apply",
            "application process",
            "application procedure",
            "application process and procedure",
            "how to apply for the scheme",
            "registration process",
        },

        "documents": {
            "documents required",
            "required documents",
            "documents needed",
            "documents required for application",
            "supporting documents",
        },
    }

    INLINE_PATTERNS = {
        "eligibility": [
            r"eligibility\s*[:\-]\s*(.+)",
            r"eligible beneficiaries\s*[:\-]\s*(.+)",
            r"who can apply\s*[:\-]\s*(.+)",
        ],

        "benefits": [
            r"benefits?\s*[:\-]\s*(.+)",
            r"financial assistance\s*[:\-]\s*(.+)",
            r"assistance provided\s*[:\-]\s*(.+)",
        ],

        "application_process": [
            r"how to apply\s*[:\-]\s*(.+)",
            r"application process\s*[:\-]\s*(.+)",
            r"application procedure\s*[:\-]\s*(.+)",
            r"registration process\s*[:\-]\s*(.+)",
        ],

        "documents": [
            r"documents required\s*[:\-]\s*(.+)",
            r"required documents\s*[:\-]\s*(.+)",
            r"supporting documents\s*[:\-]\s*(.+)",
        ],
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

        result = {
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

        # Fallback:
        # some government sites put labels inline
        # instead of using proper headings.
        for key in result:
            if not result[key]:
                result[key] = self._extract_inline(
                    cleaned_text,
                    key,
                )

        return result

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

        collected: dict[
            str,
            list[str]
        ] = {
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
                collected[
                    current_section
                ].append(line)

        return {
            section: self._join_content(lines)
            for section, lines
            in collected.items()
        }

    def _identify_heading(
        self,
        line: str,
    ) -> str | None:
        normalized = self._normalize_heading(
            line
        )

        if not normalized:
            return None

        # Headings should be short enough
        # not to accidentally classify paragraphs.
        if len(normalized) > 80:
            return None

        for section, aliases in (
            self.SECTION_ALIASES.items()
        ):
            if normalized in aliases:
                return section

        return None

    def _extract_inline(
        self,
        text: str,
        section_name: str,
    ) -> str:
        patterns = self.INLINE_PATTERNS.get(
            section_name,
            [],
        )

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if not match:
                continue

            value = match.group(1).strip()

            # Avoid returning enormous chunks.
            if len(value) > 800:
                value = value[:800].strip()

            return value

        return ""

    @staticmethod
    def _normalize_heading(
        value: str,
    ) -> str:
        value = str(value).lower().strip()

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