from __future__ import annotations

import re
from typing import Any


class OfficialContentExtractionService:
    """
    Extracts useful scheme information from cleaned text
    obtained from official government pages.

    Extraction strategy:

    1. Structured heading-based extraction
    2. Inline label extraction
    3. Sentence-level factual fallback

    The service only extracts text that already exists
    in the official source. It does not generate or infer
    scheme information.
    """

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
            r"(?:^|\n)\s*eligibility\s*[:\-]\s*(.+)",
            r"(?:^|\n)\s*eligible beneficiaries\s*[:\-]\s*(.+)",
            r"(?:^|\n)\s*who can apply\s*[:\-]\s*(.+)",
        ],

        "benefits": [
            r"(?:^|\n)\s*benefits?\s*[:\-]\s*(.+)",
            r"(?:^|\n)\s*financial assistance\s*[:\-]\s*(.+)",
            r"(?:^|\n)\s*assistance provided\s*[:\-]\s*(.+)",
        ],

        "application_process": [
            r"(?:^|\n)\s*how to apply\s*[:\-]\s*(.+)",
            r"(?:^|\n)\s*application process\s*[:\-]\s*(.+)",
            r"(?:^|\n)\s*application procedure\s*[:\-]\s*(.+)",
            r"(?:^|\n)\s*registration process\s*[:\-]\s*(.+)",
        ],

        "documents": [
            r"(?:^|\n)\s*documents required\s*[:\-]\s*(.+)",
            r"(?:^|\n)\s*required documents\s*[:\-]\s*(.+)",
            r"(?:^|\n)\s*supporting documents\s*[:\-]\s*(.+)",
        ],
    }

    # Sentence-level signals are intentionally conservative.
    # These are only used when proper sections and inline
    # labels were not found.
    SENTENCE_SIGNALS = {
        "benefits": (
            "provides grant",
            "grant funding",
            "financial assistance",
            "financial support",
            "provides assistance",
            "provides support",
            "benefit",
            "subsidy",
            "reimbursement",
            "grant-in-aid",
            "grant in aid",
        ),

        "eligibility": (
            "eligible",
            "eligibility",
            "applicant must",
            "beneficiary must",
            "shall be eligible",
            "can apply",
            "may apply",
            "eligible applicant",
            "eligible beneficiary",
        ),

        "application_process": (
            "apply through",
            "apply online",
            "apply offline",
            "application can be",
            "applications can be",
            "application shall",
            "application must be",
            "register through",
            "registration through",
            "submit the application",
            "application form",
        ),

        "documents": (
            "documents required",
            "required documents",
            "supporting documents",
            "aadhaar",
            "aadhar",
            "bank account details",
            "certificate required",
            "identity proof",
            "income certificate",
        ),
    }

    def extract(
        self,
        text: str,
    ) -> dict[str, Any]:
        cleaned_text = self._clean_text(
            text
        )

        if not cleaned_text:
            return self._empty_result()

        # ---------------------------------------------
        # Level 1:
        # Proper heading-based extraction
        # ---------------------------------------------

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

        # ---------------------------------------------
        # Level 2:
        # Inline labels
        #
        # Example:
        # Eligibility: Farmers above 18 years...
        # ---------------------------------------------

        for key in result:
            if not result[key]:
                result[key] = (
                    self._extract_inline(
                        cleaned_text,
                        key,
                    )
                )

        # ---------------------------------------------
        # Level 3:
        # Sentence-level fallback
        #
        # Real government websites often describe
        # benefits/eligibility inside normal paragraphs
        # instead of clean headings.
        # ---------------------------------------------

        sentence_fallbacks = (
            self._extract_sentence_fallbacks(
                cleaned_text
            )
        )

        for key in result:
            if not result[key]:
                result[key] = (
                    sentence_fallbacks.get(
                        key,
                        "",
                    )
                )

        return result

    @staticmethod
    def _clean_text(
        text: str,
    ) -> str:
        value = str(
            text or ""
        )

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
            list[str],
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
            section: self._join_content(
                section_lines
            )
            for section, section_lines
            in collected.items()
        }

    def _identify_heading(
        self,
        line: str,
    ) -> str | None:
        normalized = (
            self._normalize_heading(
                line
            )
        )

        if not normalized:
            return None

        # Prevent normal paragraphs from being
        # mistaken for section headings.
        if len(normalized) > 80:
            return None

        for (
            section,
            aliases,
        ) in self.SECTION_ALIASES.items():
            if normalized in aliases:
                return section

        return None

    def _extract_inline(
        self,
        text: str,
        section_name: str,
    ) -> str:
        patterns = (
            self.INLINE_PATTERNS.get(
                section_name,
                [],
            )
        )

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE | re.MULTILINE,
            )

            if not match:
                continue

            value = (
                match.group(1)
                .strip()
            )

            # Avoid accidentally capturing a huge
            # portion of the government page.
            if len(value) > 800:
                value = (
                    value[:800]
                    .strip()
                )

            return value

        return ""

    def _extract_sentence_fallbacks(
        self,
        text: str,
    ) -> dict[str, str]:
        """
        Extract useful factual sentences when the page
        does not provide clean section headings.

        This method does not infer anything.
        It only copies sentences from the official text.
        """

        sentences = self._split_sentences(
            text
        )

        collected: dict[
            str,
            list[str],
        ] = {
            "eligibility": [],
            "benefits": [],
            "application_process": [],
            "documents": [],
        }

        for sentence in sentences:
            cleaned = sentence.strip()

            # Tiny fragments usually come from menus,
            # buttons or broken HTML.
            if len(cleaned) < 20:
                continue

            # Avoid enormous malformed chunks.
            if len(cleaned) > 1200:
                continue

            lowered = cleaned.lower()

            for (
                section,
                signals,
            ) in self.SENTENCE_SIGNALS.items():

                if not any(
                    signal in lowered
                    for signal in signals
                ):
                    continue

                collected[
                    section
                ].append(cleaned)

        return {
            section: self._join_unique_sentences(
                sentences
            )
            for section, sentences
            in collected.items()
        }

    @staticmethod
    def _split_sentences(
            text: str,
    ) -> list[str]:
        text = str(text or "").strip()

        if not text:
            return []

        # Preserve common abbreviations so that:
        #
        # "Rs. 40 crore"
        #
        # does not become two separate sentences.
        abbreviation_map = {
            "Rs.": "Rs<PERIOD>",
            "rs.": "rs<PERIOD>",
            "Mr.": "Mr<PERIOD>",
            "Mrs.": "Mrs<PERIOD>",
            "Dr.": "Dr<PERIOD>",
            "No.": "No<PERIOD>",
            "Govt.": "Govt<PERIOD>",
        }

        for original, protected in (
                abbreviation_map.items()
        ):
            text = text.replace(
                original,
                protected,
            )

        # Preserve paragraph boundaries.
        text = re.sub(
            r"\n\s*\n+",
            " __PARAGRAPH__ ",
            text,
        )

        # Ordinary line wrapping is not a
        # sentence boundary.
        text = re.sub(
            r"\n+",
            " ",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        text = text.replace(
            "__PARAGRAPH__",
            ". ",
        )

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text,
        )

        result = []

        for sentence in sentences:
            sentence = sentence.replace(
                "<PERIOD>",
                ".",
            ).strip()

            if sentence:
                result.append(sentence)

        return result

    @staticmethod
    def _join_unique_sentences(
        sentences: list[str],
        limit: int = 3,
    ) -> str:
        """
        Remove duplicate extracted sentences and keep
        only a small number of high-signal statements.
        """

        unique: list[str] = []

        seen: set[str] = set()

        for sentence in sentences:
            normalized = re.sub(
                r"\s+",
                " ",
                sentence,
            ).strip()

            key = normalized.lower()

            if not normalized:
                continue

            if key in seen:
                continue

            seen.add(key)

            unique.append(
                normalized
            )

            if len(unique) >= limit:
                break

        return " ".join(
            unique
        )

    @staticmethod
    def _normalize_heading(
        value: str,
    ) -> str:
        value = (
            str(value)
            .lower()
            .strip()
        )

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

        text = " ".join(
            lines
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    @staticmethod
    def _empty_result(
    ) -> dict[str, str]:
        return {
            "eligibility": "",
            "benefits": "",
            "application_process": "",
            "documents": "",
        }


official_content_extractor = (
    OfficialContentExtractionService()
)