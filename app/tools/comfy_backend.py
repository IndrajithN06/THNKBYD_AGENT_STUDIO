"""ComfyUI image generation backend."""

import shutil
from pathlib import Path

from app.config.settings import Settings
from app.tools.comfy_client import ComfyClient
from app.tools.image_service import ImageGenerationError


class ComfyBackend:
    """Image backend implementation using ComfyUI."""

    def __init__(self, settings: Settings) -> None:

        self._client = ComfyClient()

        self._workflow_path = settings.workflows_dir / "dreamshaper_workflow.json"

    def generate(
        self,
        prompt: str,
        output_path: Path,
    ) -> Path:
        """
        Generate an image using ComfyUI and save it to output_path.
        """

        try:

            # Load workflow
            workflow = self._client.load_workflow(str(self._workflow_path))

            # Inject prompt
            workflow = self._client.update_prompt(
                workflow,
                prompt,
            )

            # Queue prompt
            response = self._client.queue_prompt(workflow)

            prompt_id = response.get("prompt_id")

            if not prompt_id:
                raise ImageGenerationError("ComfyUI did not return a prompt_id.")

            # Wait for generation
            generated_images = self._client.wait_for_image(prompt_id)

            if not generated_images:
                raise ImageGenerationError("ComfyUI did not generate any images.")

            generated_image = Path(generated_images[0])

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                generated_image,
                output_path,
            )

            return output_path

        except Exception as exc:

            raise ImageGenerationError(f"ComfyUI generation failed: {exc}") from exc
