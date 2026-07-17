"""Image Prompt agent — transforms a storyboard into image generation prompts."""

import logging
import re
from time import perf_counter
from typing import Protocol

from pydantic import ValidationError

from app.models.image_prompt import ImagePromptResult
from app.models.storyboard import StoryboardResult
from app.tools.llm_client import LLMProvider
from app.tools.resource_loader import ResourceLoader

logger = logging.getLogger(__name__)

IMAGE_PROMPT_SYSTEM_PROMPT_FILE = "image_prompt_system_prompt.md"
STYLE_GUIDE_FILE = "style.md"

SCENE_HEADING_PATTERN = re.compile(
    r"^#{1,6}\s*scene\s+\d+\b",
    re.IGNORECASE | re.MULTILINE,
)


class ImagePromptGenerator(Protocol):
    """Contract for agents that transform storyboards into image prompts."""

    def generate(
        self,
        storyboard: StoryboardResult,
    ) -> ImagePromptResult:
        """Convert a storyboard into image generation prompts."""
        ...


class ImagePromptAgent:
    """Composes image prompt requests and delegates generation to the LLM provider."""

    def __init__(
        self,
        llm: LLMProvider,
        resource_loader: ResourceLoader,
    ) -> None:
        self._llm = llm
        self._resources = resource_loader

    def generate(
        self,
        storyboard: StoryboardResult,
    ) -> ImagePromptResult:
        """Transform storyboard markdown into validated image prompts."""

        logger.info("Image prompt generation started")
        started_at = perf_counter()

        system_prompt = self._resources.load_prompt(IMAGE_PROMPT_SYSTEM_PROMPT_FILE)
        logger.debug("Image prompt system prompt loaded")

        style_guide = self._resources.load_knowledge(STYLE_GUIDE_FILE)
        logger.debug("Style guide loaded")

        prompt = self._compose_prompt(
            system_prompt,
            style_guide,
            storyboard.storyboard_markdown,
        )

        logger.info("Image prompt LLM request")
        markdown = self._llm.generate(prompt)
        logger.info("Image prompt LLM response received")

        try:
            result = ImagePromptResult(
                image_prompt_markdown=markdown,
                scene_count=len(SCENE_HEADING_PATTERN.findall(markdown)),
                generation_time_ms=(perf_counter() - started_at) * 1000,
            )
        except ValidationError:
            logger.exception("Image prompt validation failed")
            raise

        logger.info(
            "Image prompt generation completed (%d scenes)",
            result.scene_count,
        )

        return result

    @staticmethod
    def _compose_prompt(
        system_prompt: str,
        style_guide: str,
        storyboard: str,
    ) -> str:
        return (
            f"{system_prompt}\n\n---\n\n"
            f"# THNKBYD Style Guide\n\n{style_guide}\n\n---\n\n"
            f"# Generated Storyboard\n\n{storyboard}\n\n---\n\n"
            "Convert this storyboard into professional AI image prompts."
        )
