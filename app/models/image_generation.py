"""Pydantic models for image generation."""

from pathlib import Path

from pydantic import BaseModel, Field


class GeneratedImage(BaseModel):
    """A single generated image for one storyboard scene."""

    scene_number: int = Field(ge=1)
    prompt: str = Field(min_length=1)
    image_path: Path


class ImageGenerationResult(BaseModel):
    """Output of a completed image generation run."""

    output_dir: Path
    images: list[GeneratedImage] = Field(default_factory=list)
    image_count: int = Field(ge=0)
    generation_time_ms: float = Field(ge=0)
