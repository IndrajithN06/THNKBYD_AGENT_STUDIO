"""Application entry point."""

import logging

from rich.console import Console

from app.agents.director import DirectorAgent
from app.agents.image_generator import ImageGeneratorAgent
from app.agents.image_prompt_writer import ImagePromptAgent
from app.agents.script_writer import ScriptWriterAgent
from app.agents.storyboard_writer import StoryboardAgent
from app.config.logging_config import setup_logging
from app.config.settings import Settings, get_settings
from app.tools.file_writer import FileWriter
from app.tools.image_service import HuggingFaceBackend, ImageService
from app.tools.llm_client import LLMClient
from app.tools.resource_loader import ResourceLoader

logger = logging.getLogger(__name__)


def build_director(settings: Settings, console: Console) -> DirectorAgent:
    """Wire dependencies and return a configured Director agent."""

    # Shared infrastructure
    resource_loader = ResourceLoader(
        prompts_dir=settings.prompts_dir,
        knowledge_dir=settings.knowledge_dir,
    )

    llm = LLMClient(settings)
    file_writer = FileWriter(output_dir=settings.output_dir)

    # Content generation agents
    script_writer = ScriptWriterAgent(
        llm=llm,
        resource_loader=resource_loader,
    )

    storyboard_writer = StoryboardAgent(
        llm=llm,
        resource_loader=resource_loader,
    )

    image_prompt_writer = ImagePromptAgent(
        llm=llm,
        resource_loader=resource_loader,
    )

    # Image generation
    image_backend = HuggingFaceBackend(settings)
    image_service = ImageService(backend=image_backend)

    image_generator = ImageGeneratorAgent(
        image_service=image_service,
        output_dir=settings.output_dir,
    )

    return DirectorAgent(
        settings=settings,
        script_writer=script_writer,
        storyboard_writer=storyboard_writer,
        image_prompt_writer=image_prompt_writer,
        image_generator=image_generator,
        file_writer=file_writer,
        resource_loader=resource_loader,
        console=console,
    )


def main() -> None:
    """Bootstrap dependencies and run the Director agent."""

    settings = get_settings()
    setup_logging(settings.log_level)

    console = Console()

    logger.info(
        "Starting %s (%s)",
        settings.app_name,
        settings.app_env,
    )

    director = build_director(settings, console)

    topic = console.input("\n[bold cyan]Enter video topic:[/bold cyan] ").strip()

    director.run(topic)


if __name__ == "__main__":
    main()
