"""ImageGenerator agent — turns image prompt markdown into generated PNG files."""

import logging
import re
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Protocol

from pydantic import ValidationError

from app.models.image_generation import GeneratedImage, ImageGenerationResult
from app.tools.image_service import ImageGenerationError, ImageService

logger = logging.getLogger(__name__)

SCENE_PATTERN = re.compile(
    r"^#\s*Scene\s+(\d+).*?(?=^#\s*Scene\s+\d+|\Z)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)
IMAGE_PROMPT_SECTION_PATTERN = re.compile(
    r"##\s*Image Prompt\s*\n+(.*?)(?=\n##|\Z)",
    re.IGNORECASE | re.DOTALL,
)


class ImageGenerator(Protocol):
    """Contract for agents that turn image prompt markdown into generated images."""

    def generate(self, image_prompt_markdown: str) -> ImageGenerationResult:
        """Generate one image per storyboard scene."""
        ...


class ImageGeneratorAgent:
    """Parses image prompts scene-by-scene and delegates rendering to the ImageService."""

    def __init__(self, image_service: ImageService, output_dir: Path) -> None:
        self._image_service = image_service
        self._images_root = output_dir / "images"

    def generate(self, image_prompt_markdown: str) -> ImageGenerationResult:
        """Generate a PNG for every scene and return their file paths."""

        logger.info("Image generation started")
        started_at = perf_counter()

        scene_prompts = self._extract_scene_prompts(image_prompt_markdown)
        if not scene_prompts:
            logger.warning("No scenes found in image prompt markdown")

        run_dir = self._images_root / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        images: list[GeneratedImage] = []
        for scene_number, prompt in scene_prompts:
            output_path = run_dir / f"scene_{scene_number:02d}.png"

            logger.info("Generating image for scene %d", scene_number)
            try:
                saved_path = self._image_service.generate(prompt, output_path)
            except ImageGenerationError:
                logger.exception("Image generation failed for scene %d", scene_number)
                raise

            images.append(
                GeneratedImage(
                    scene_number=scene_number, prompt=prompt, image_path=saved_path
                )
            )

        try:
            result = ImageGenerationResult(
                output_dir=run_dir,
                images=images,
                image_count=len(images),
                generation_time_ms=(perf_counter() - started_at) * 1000,
            )
        except ValidationError:
            logger.exception("Image generation result validation failed")
            raise

        logger.info("Image generation completed (%d images)", result.image_count)
        return result

    @staticmethod
    def _extract_scene_prompts(markdown: str) -> list[tuple[int, str]]:
        """Pull (scene_number, image_prompt_text) pairs out of the prompt markdown."""
        scenes: list[tuple[int, str]] = []

        for match in SCENE_PATTERN.finditer(markdown):
            scene_number = int(match.group(1))
            prompt_match = IMAGE_PROMPT_SECTION_PATTERN.search(match.group(0))

            if not prompt_match:
                logger.warning(
                    "Scene %d has no Image Prompt section; skipping", scene_number
                )
                continue

            prompt_text = prompt_match.group(1).strip()
            if prompt_text:
                scenes.append((scene_number, prompt_text))

        return scenes
