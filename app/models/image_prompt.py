"""Pydantic models for image prompt generation."""

from pydantic import BaseModel, Field


class ImagePromptResult(BaseModel):
    """Output of a completed image prompt generation run."""

    image_prompt_markdown: str = Field(min_length=1)
    scene_count: int = Field(ge=1)
    generation_time_ms: float = Field(ge=0)
