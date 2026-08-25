from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup


class HTMLStructureExtractionService:
    """
    Extracts scheme information directly from common
    HTML structures used by government websites.

    Supported structures:
    - tables
    - definition lists
    - labelled blocks/cards
    - accordion-like sections

    This service does not generate information.
    It only copies text present in the source HTML.
    """

    FIELD_ALIASES = {
        "eligibility": {
            "eligibility",
            "eligibility criteria",
            "who can apply",
            "eligible beneficiaries",
            "beneficiaries",
        },

        "benefits": {
            "benefits",
            "scheme benefits",
            "financial assistance",
            "financial benefits",
            "assistance",
        },

        "application_process": {
            "how to apply",
            "application process",
            "application procedure",
            "registration process",
        },

        "documents": {
            "documents required",
            "required documents",
            "documents",
            "supporting documents",
        },
    }

    def extract(
        self,
        html: str,
    ) -> dict[str, str]:
        soup = BeautifulSoup(
            str(html or ""),
            "html.parser",
        )

        result = self._empty_result()

        self._extract_tables(
            soup,
            result,
        )

        self._extract_definition_lists(
            soup,
            result,
        )

        self._extract_labelled_blocks(
            soup,
            result,
        )

        return result

    def _extract_tables(
        self,
        soup: BeautifulSoup,
        result: dict[str, str],
    ) -> None:
        for row in soup.find_all("tr"):
            cells = row.find_all(
                ["th", "td"]
            )

            if len(cells) < 2:
                continue

            label = cells[0].get_text(
                " ",
                strip=True,
            )

            value = " ".join(
                cell.get_text(
                    " ",
                    strip=True,
                )
                for cell in cells[1:]
            )

            self._store_if_matching(
                result=result,
                label=label,
                value=value,
            )

    def _extract_definition_lists(
        self,
        soup: BeautifulSoup,
        result: dict[str, str],
    ) -> None:
        for dt in soup.find_all("dt"):
            label = dt.get_text(
                " ",
                strip=True,
            )

            dd = dt.find_next_sibling(
                "dd"
            )

            if dd is None:
                continue

            value = dd.get_text(
                " ",
                strip=True,
            )

            self._store_if_matching(
                result=result,
                label=label,
                value=value,
            )

    def _extract_labelled_blocks(
        self,
        soup: BeautifulSoup,
        result: dict[str, str],
    ) -> None:
        candidates = soup.find_all(
            [
                "div",
                "section",
                "article",
                "li",
            ]
        )

        for element in candidates:
            heading = element.find(
                [
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "strong",
                    "b",
                ]
            )

            if heading is None:
                continue

            label = heading.get_text(
                " ",
                strip=True,
            )

            field = self._match_field(
                label
            )

            if field is None:
                continue

            # Work on a copy-like textual view by
            # collecting siblings/content after label.
            text = element.get_text(
                " ",
                strip=True,
            )

            heading_text = heading.get_text(
                " ",
                strip=True,
            )

            value = text

            if value.lower().startswith(
                heading_text.lower()
            ):
                value = value[
                    len(heading_text):
                ].strip(
                    " :-–—"
                )

            if not value:
                continue

            self._merge_value(
                result,
                field,
                value,
            )

    def _store_if_matching(
        self,
        *,
        result: dict[str, str],
        label: str,
        value: str,
    ) -> None:
        field = self._match_field(
            label
        )

        if field is None:
            return

        value = self._clean_value(
            value
        )

        if not value:
            return

        self._merge_value(
            result,
            field,
            value,
        )

    def _match_field(
        self,
        label: str,
    ) -> str | None:
        normalized = self._normalize_label(
            label
        )

        if not normalized:
            return None

        for field, aliases in (
            self.FIELD_ALIASES.items()
        ):
            if normalized in aliases:
                return field

        return None

    @staticmethod
    def _merge_value(
        result: dict[str, str],
        field: str,
        value: str,
    ) -> None:
        value = re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

        if not value:
            return

        existing = result.get(
            field,
            "",
        ).strip()

        if not existing:
            result[field] = value
            return

        if value.lower() in existing.lower():
            return

        result[field] = (
            f"{existing} {value}"
        ).strip()

    @staticmethod
    def _normalize_label(
        value: str,
    ) -> str:
        value = str(
            value or ""
        ).lower().strip()

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
    def _clean_value(
        value: str,
    ) -> str:
        return re.sub(
            r"\s+",
            " ",
            str(value or ""),
        ).strip()

    @staticmethod
    def _empty_result() -> dict[str, str]:
        return {
            "eligibility": "",
            "benefits": "",
            "application_process": "",
            "documents": "",
        }


html_structure_extractor = (
    HTMLStructureExtractionService()
)
