"""Storyboard agent — transforms a completed script into storyboard markdown."""

import logging
import re
from time import perf_counter
from typing import Protocol

from pydantic import ValidationError

from app.models.storyboard import StoryboardResult
from app.tools.llm_client import LLMProvider
from app.tools.resource_loader import ResourceLoader

logger = logging.getLogger(__name__)

STORYBOARD_SYSTEM_PROMPT_FILE = "storyboard_system_prompt.md"
STYLE_GUIDE_FILE = "style.md"
SCENE_HEADING_PATTERN = re.compile(r"^#{1,6}\s*scene\s+\d+\b", re.IGNORECASE | re.MULTILINE)
TITLE_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)


class StoryboardGenerator(Protocol):
    """Contract for agents that transform scripts into storyboards."""

    def generate(self, script: str) -> StoryboardResult:
        """Convert a generated script into a storyboard result."""
        ...


class StoryboardAgent:
    """Composes storyboard prompts and delegates generation to the LLM provider."""

    def __init__(self, llm: LLMProvider, resource_loader: ResourceLoader) -> None:
        self._llm = llm
        self._resources = resource_loader

    def generate(self, script: str) -> StoryboardResult:
        """Transform script markdown into a validated cinematic storyboard."""
        logger.info("Storyboard generation started")
        started_at = perf_counter()

        system_prompt = self._resources.load_prompt(STORYBOARD_SYSTEM_PROMPT_FILE)
        logger.debug("Storyboard prompt loaded")
        style_guide = self._resources.load_knowledge(STYLE_GUIDE_FILE)
        logger.debug("Style guide loaded")
        prompt = self._compose_prompt(system_prompt, style_guide, script)

        logger.info("Storyboard LLM request")
        markdown = self._llm.generate(prompt)
        logger.info("Storyboard LLM response received")

        try:
            result = StoryboardResult(
                title=self._extract_title(markdown),
                storyboard_markdown=markdown,
                scene_count=len(SCENE_HEADING_PATTERN.findall(markdown)),
                generation_time_ms=(perf_counter() - started_at) * 1000,
            )
        except ValidationError:
            logger.exception("Storyboard result validation failed")
            raise

        logger.info("Storyboard generation completed (%d scenes)", result.scene_count)
        return result

    @staticmethod
    def _compose_prompt(system_prompt: str, style_guide: str, script: str) -> str:
        return (
            f"{system_prompt}\n\n---\n\n"
            f"# THNKBYD Style Guide\n\n{style_guide}\n\n---\n\n"
            f"# Generated Script\n\n{script}\n\n---\n\n"
            "Convert this script into a professional cinematic storyboard."
        )

    @staticmethod
    def _extract_title(markdown: str) -> str:
        match = TITLE_PATTERN.search(markdown)
        return match.group(1).strip() if match else "THNKBYD Storyboard"
