"""Low-level client for communicating with ComfyUI."""

import json
import os
import time

import requests


class ComfyClient:
    """Client for interacting with the ComfyUI HTTP API."""

    def __init__(self) -> None:

        self.base_url = "http://127.0.0.1:8188"

        # ComfyUI's own output folder
        self.comfy_output_dir = r"C:\VideoEditing\ComfyUI\ComfyUI\output"

    def load_workflow(self, workflow_path: str) -> dict:
        """Load a ComfyUI API workflow."""

        with open(workflow_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def update_prompt(
        self,
        workflow: dict,
        prompt: str,
    ) -> dict:
        """Replace the positive prompt."""

        workflow["2"]["inputs"]["text"] = prompt

        return workflow

    def queue_prompt(
        self,
        workflow: dict,
    ) -> dict:
        """Queue a workflow for execution."""

        response = requests.post(
            f"{self.base_url}/prompt",
            json={"prompt": workflow},
        )

        response.raise_for_status()

        return response.json()

    def get_history(
        self,
        prompt_id: str,
    ) -> dict:
        """Retrieve execution history."""

        response = requests.get(f"{self.base_url}/history/{prompt_id}")

        response.raise_for_status()

        return response.json()

    def wait_for_image(
        self,
        prompt_id: str,
    ) -> list[str]:
        """Wait until generation completes and return generated image paths."""

        print("\nWaiting for image generation...")

        while True:

            history = self.get_history(prompt_id)

            if prompt_id in history:

                result = history[prompt_id]

                if result["status"]["completed"]:

                    print("Generation completed!")

                    image_paths = []

                    for node_output in result["outputs"].values():

                        if "images" not in node_output:
                            continue

                        for image in node_output["images"]:

                            filename = image["filename"]

                            subfolder = image.get(
                                "subfolder",
                                "",
                            )

                            image_paths.append(
                                os.path.join(
                                    self.comfy_output_dir,
                                    subfolder,
                                    filename,
                                )
                            )

                    return image_paths

            print("Still generating...")

            time.sleep(3)
