import json
import time
import requests
import os
import shutil
from pathlib import Path


class ComfyClient:

    def __init__(self):

        self.base_url = "http://127.0.0.1:8188"

        # ComfyUI generated output location
        self.comfy_output_dir = r"C:\VideoEditing\ComfyUI\ComfyUI\output"

        # THNKBYD project output/images
        project_root = Path(__file__).resolve().parents[2]

        self.thnkbyd_output_dir = project_root / "outputs" / "images"

        self.thnkbyd_output_dir.mkdir(parents=True, exist_ok=True)

    def load_workflow(self, workflow_path):

        with open(workflow_path, "r", encoding="utf-8") as file:

            return json.load(file)

    def update_prompt(self, workflow, prompt):
        """
        Updates positive prompt node in ComfyUI workflow.
        Node 2 = CLIPTextEncode positive prompt
        """

        workflow["2"]["inputs"]["text"] = prompt

        return workflow

    def queue_prompt(self, workflow):

        url = f"{self.base_url}/prompt"

        payload = {"prompt": workflow}

        response = requests.post(url, json=payload)

        response.raise_for_status()

        return response.json()

    def get_history(self, prompt_id):

        url = f"{self.base_url}/history/{prompt_id}"

        response = requests.get(url)

        response.raise_for_status()

        return response.json()

    def wait_for_image(self, prompt_id):

        print("\nWaiting for generation...")

        while True:

            history = self.get_history(prompt_id)

            if prompt_id in history:

                result = history[prompt_id]

                if result["status"]["completed"]:

                    print("Generation completed!")

                    images = []

                    for node_output in result["outputs"].values():

                        if "images" in node_output:

                            images.extend(node_output["images"])

                    output_images = []

                    for image in images:

                        filename = image["filename"]

                        subfolder = image.get("subfolder", "")

                        # Original ComfyUI image
                        source_path = os.path.join(
                            self.comfy_output_dir, subfolder, filename
                        )

                        # THNKBYD image location
                        destination_path = self.thnkbyd_output_dir / filename

                        shutil.copy(source_path, destination_path)

                        output_images.append(str(destination_path))

                    return output_images

            print("Still generating...")

            time.sleep(3)
