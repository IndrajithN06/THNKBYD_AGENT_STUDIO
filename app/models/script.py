"""Pydantic models for script generation."""

from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class ScriptRequest(BaseModel):
    """Validated input for script generation."""

    topic: str = Field(min_length=3, max_length=200)

    @field_validator("topic")
    @classmethod
    def strip_and_validate(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Topic cannot be empty or whitespace.")
        return cleaned


class ScriptResult(BaseModel):
    """Output of a completed script generation run."""

    topic: str
    content: str
    filepath: Path
