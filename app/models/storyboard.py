"""Pydantic models for storyboard generation."""

from pydantic import BaseModel, Field


class StoryboardResult(BaseModel):
    """Output of a completed storyboard generation run."""

    title: str = Field(min_length=1)
    storyboard_markdown: str = Field(min_length=1)
    scene_count: int = Field(ge=1)
    generation_time_ms: float = Field(ge=0)
