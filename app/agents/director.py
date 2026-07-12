"""Director agent — orchestrates the script generation workflow."""

import logging

from pydantic import ValidationError
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from app.agents.script_writer import ScriptGenerator
from app.config.settings import Settings
from app.models.script import ScriptRequest, ScriptResult
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
        file_writer: FileWriter,
        resource_loader: ResourceLoader,
        console: Console,
    ) -> None:
        self._settings = settings
        self._script_writer = script_writer
        self._file_writer = file_writer
        self._resources = resource_loader
        self._console = console

    def run(self, topic: str) -> ScriptResult | None:
        """Execute the full script generation pipeline."""
        self._console.print(
            Panel.fit(
                f"[bold]{self._settings.app_name}[/bold] — Script Generation",
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
        except OSError as exc:
            self._console.print(f"\n[red]File error:[/red] {exc}")
            logger.error("File operation failed: %s", exc)
            return None
        except FileNotFoundError as exc:
            self._console.print(f"\n[red]Missing resource:[/red] {exc}")
            logger.error("Resource loading failed: %s", exc)
            return None

    def _execute_pipeline(self, request: ScriptRequest) -> ScriptResult:
        """Run generation and persistence steps for a validated request."""
        with self._console.status("[bold green]Loading THNKBYD style guide..."):
            style_guide = self._resources.load_knowledge(STYLE_GUIDE_FILE)
            logger.debug("Style guide loaded")

        with self._console.status("[bold green]Generating script..."):
            content = self._script_writer.generate(request, style_guide)

        with self._console.status("[bold green]Saving markdown to outputs/scripts/..."):
            filepath = self._file_writer.save_script(request.topic, content)

        self._console.print()
        self._console.print(Markdown(content))
        self._console.print(f"\n[green]Saved[/green] → [bold]{filepath}[/bold]")

        logger.info("Pipeline complete for topic: %s", request.topic)
        return ScriptResult(topic=request.topic, content=content, filepath=filepath)

    def _validate_topic(self, topic: str) -> ScriptRequest | None:
        """Validate and parse the topic input."""
        try:
            return ScriptRequest(topic=topic)
        except ValidationError as exc:
            message = exc.errors()[0]["msg"]
            self._console.print(f"[red]Invalid topic:[/red] {message}")
            logger.warning("Topic validation failed: %s", message)
            return None
