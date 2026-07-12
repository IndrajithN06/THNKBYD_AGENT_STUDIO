"""Director agent — orchestrates the script generation workflow."""

import logging

from pydantic import ValidationError
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from app.agents.script_writer import ScriptGenerator
from app.agents.storyboard_writer import StoryboardGenerator
from app.config.settings import Settings
from app.models.script import ScriptRequest
from app.models.storyboard import StoryboardResult
from app.tools.file_writer import FileWriter
from app.tools.llm_client import LLMError
from app.tools.resource_loader import ResourceLoader

logger = logging.getLogger(__name__)

STYLE_GUIDE_FILE = "style.md"


class DirectorAgent:
    """Receives a topic, coordinates generation, saves output, and reports progress."""

    def __init__(
        self,
        settings: Settings,
        script_writer: ScriptGenerator,
        storyboard_writer: StoryboardGenerator,
        file_writer: FileWriter,
        resource_loader: ResourceLoader,
        console: Console,
    ) -> None:
        self._settings = settings
        self._script_writer = script_writer
        self._storyboard_writer = storyboard_writer
        self._file_writer = file_writer
        self._resources = resource_loader
        self._console = console

    def run(self, topic: str) -> StoryboardResult | None:
        """Execute the script-to-storyboard generation pipeline."""
        self._console.print(
            Panel.fit(
                f"[bold]{self._settings.app_name}[/bold] — Storyboard Generation",
                border_style="green",
            )
        )

        request = self._validate_topic(topic)
        if request is None:
            return None

        try:
            return self._execute_pipeline(request)
        except LLMError as exc:
            self._console.print(f"\n[red]Generation failed:[/red] {exc}")
            logger.error("Script generation failed: %s", exc)
            return None
        except FileNotFoundError as exc:
            self._console.print(f"\n[red]Missing resource:[/red] {exc}")
            logger.error("Resource loading failed: %s", exc)
            return None
        except OSError as exc:
            self._console.print(f"\n[red]File error:[/red] {exc}")
            logger.error("File operation failed: %s", exc)
            return None
        except ValidationError as exc:
            self._console.print("\n[red]Storyboard validation failed.[/red]")
            logger.error("Storyboard validation failed: %s", exc)
            return None

    def _execute_pipeline(self, request: ScriptRequest) -> StoryboardResult:
        """Run generation and persistence steps for a validated request."""
        with self._console.status("[bold green]Loading THNKBYD style guide..."):
            style_guide = self._resources.load_knowledge(STYLE_GUIDE_FILE)
            logger.debug("Style guide loaded")

        with self._console.status("[bold green]Generating script..."):
            content = self._script_writer.generate(request, style_guide)

        with self._console.status("[bold green]Generating cinematic storyboard..."):
            storyboard = self._storyboard_writer.generate(content)

        with self._console.status("[bold green]Saving markdown to outputs/storyboards/..."):
            filepath = self._file_writer.save_storyboard(
                request.topic, storyboard.storyboard_markdown
            )

        self._console.print()
        self._console.print(Markdown(storyboard.storyboard_markdown))
        self._console.print(f"\n[green]Saved[/green] → [bold]{filepath}[/bold]")

        logger.info("Pipeline complete for topic: %s", request.topic)
        return storyboard

    def _validate_topic(self, topic: str) -> ScriptRequest | None:
        """Validate and parse the topic input."""
        try:
            return ScriptRequest(topic=topic)
        except ValidationError as exc:
            message = exc.errors()[0]["msg"]
            self._console.print(f"[red]Invalid topic:[/red] {message}")
            logger.warning("Topic validation failed: %s", message)
            return None
