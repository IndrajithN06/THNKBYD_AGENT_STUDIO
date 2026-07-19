"""Backend interface and image generation service."""

from pathlib import Path
from typing import Protocol


class ImageGenerationError(Exception):
    """Raised when image generation fails."""


class ImageBackend(Protocol):
    """Contract for image generation backends."""

    def generate(
        self,
        prompt: str,
        output_path: Path,
    ) -> Path:
        """
        Generate an image from a prompt and save it to output_path.
        Returns the saved image path.
        """
        ...


class ImageService:
    """Backend-agnostic image generation service."""

    def __init__(self, backend: ImageBackend) -> None:
        self._backend = backend

    def generate(
        self,
        prompt: str,
        output_path: Path,
    ) -> Path:

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        return self._backend.generate(
            prompt=prompt,
            output_path=output_path,
        )
