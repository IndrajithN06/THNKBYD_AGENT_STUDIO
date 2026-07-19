from app.tools.comfy_client import ComfyClient


def main():

    print("Testing ComfyUI connection...\n")

    client = ComfyClient()

    # Load workflow
    workflow = client.load_workflow("app/workflows/dreamshaper_workflow.json")

    print("Workflow loaded successfully")

    # Dynamic prompt
    prompt = """
Cinematic wide establishing shot of a crowded metropolitan street at dusk,
people walking quickly with subtle motion blur,
some faces showing happiness while others appear exhausted and lost,
a modern glass office tower glowing in the background,
soft golden hour lighting,
shot from a high aerial perspective,
35mm film look,
shallow depth of field,
realistic documentary style
"""

    workflow = client.update_prompt(workflow, prompt)

    print("Prompt updated successfully")

    # Send workflow
    response = client.queue_prompt(workflow)

    print("\nComfyUI response:")
    print(response)

    prompt_id = response.get("prompt_id")

    if not prompt_id:

        print("\nFailed: No prompt_id received")

        return

    print("\nPrompt ID:")
    print(prompt_id)

    # Generate and copy image
    images = client.wait_for_image(prompt_id)

    print("\nGenerated Images:")

    for image in images:

        print(image)


if __name__ == "__main__":
    main()
