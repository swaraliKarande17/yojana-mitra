from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

    @field_validator("message")
    @classmethod
    def strip_message(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message must not be empty")
        return cleaned


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)

    @field_validator("query")
    @classmethod
    def strip_query(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("query must not be empty")
        return cleaned


class SchemeSummary(BaseModel):
    id: str
    name: str
    short_name: str | None = None
    score: int
    official_source: str | None = None


class MentionedScheme(BaseModel):
    id: str
    name: str
    short_name: str | None = None


class GroundingResult(BaseModel):
    valid: bool
    recommendedSchemeIds: list[str] = Field(default_factory=list)
    mentionedSchemes: list[MentionedScheme] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    grounding: GroundingResult
    schemes: list[SchemeSummary]


class GeminiStructuredResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str = Field(min_length=1)
    recommended_scheme_ids: list[str] = Field(default_factory=list)


Scheme = dict[str, Any]