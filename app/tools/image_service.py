"""Image backend interface, Hugging Face implementation, and ImageService wrapper."""

import logging
import time
from pathlib import Path
from typing import Protocol

from huggingface_hub import InferenceClient

from app.config.settings import Settings

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2.0


class ImageGenerationError(Exception):
    """Raised when the image backend fails to generate an image."""


class ImageBackend(Protocol):
    """Contract for any image generation backend."""

    def generate(self, prompt: str) -> bytes:
        """Generate image bytes from prompt."""
        ...


class HuggingFaceBackend:
    """
    Hugging Face Inference Providers backend.
    Uses provider routing like:
    provider="fal-ai"
    """

    def __init__(self, settings: Settings) -> None:

        if not settings.huggingface_api_key:
            logger.warning(
                "HUGGINGFACE_API_KEY is not set; image generation will fail."
            )

        self._client = InferenceClient(
            provider="fal-ai",
            api_key=settings.huggingface_api_key,
        )

        self._model = settings.huggingface_image_model

    def generate(self, prompt: str) -> bytes:
        """
        Generate image using Hugging Face Inference Providers.
        Returns raw image bytes.
        """

        logger.info("Generating image using model: %s", self._model)

        try:

            image = self._client.text_to_image(prompt, model=self._model)

            # PIL Image -> PNG bytes
            from io import BytesIO

            buffer = BytesIO()

            image.save(buffer, format="PNG")

            return buffer.getvalue()

        except Exception as exc:

            logger.exception("Hugging Face image generation failed")

            raise ImageGenerationError(
                f"Hugging Face generation failed: {exc}"
            ) from exc


class ImageService:
    """Backend-agnostic image generation service."""

    def __init__(self, backend: ImageBackend) -> None:
        self._backend = backend

    def generate(self, prompt: str, output_path: Path) -> Path:

        last_error = None

        for attempt in range(1, MAX_RETRIES + 1):

            try:

                image_bytes = self._backend.generate(prompt)

                output_path.parent.mkdir(parents=True, exist_ok=True)

                output_path.write_bytes(image_bytes)

                logger.info("Image saved: %s", output_path)

                return output_path

            except ImageGenerationError as exc:

                last_error = exc

                logger.warning("Attempt %d/%d failed: %s", attempt, MAX_RETRIES, exc)

                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SECONDS * attempt)

        raise ImageGenerationError(
            f"Image generation failed after {MAX_RETRIES} attempts"
        ) from last_error
