"""ScriptWriter agent — loads prompts, calls the LLM, returns markdown."""

import logging
from time import perf_counter
from typing import Protocol

from app.models.script import ScriptRequest, ScriptResult
from app.tools.llm_client import LLMProvider
from app.tools.resource_loader import ResourceLoader

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_FILE = "system_prompt.md"
SCRIPT_PROMPT_FILE = "script_prompt.md"


class ScriptGenerator(Protocol):
    """Contract for agents that produce script markdown from a topic."""

    def generate(self, request: ScriptRequest, style_guide: str) -> ScriptResult:
        """Generate a validated script result."""
        ...


class ScriptWriterAgent:
    """Generates a YouTube script by composing prompts and calling the LLM."""

    def __init__(self, llm: LLMProvider, resource_loader: ResourceLoader) -> None:
        self._llm = llm
        self._resources = resource_loader

    def generate(self, request: ScriptRequest, style_guide: str) -> ScriptResult:
        """Build the full prompt, call the LLM, and return a ScriptResult."""

        logger.info("Generating script for topic: %s", request.topic)

        started_at = perf_counter()

        system_prompt = self._resources.load_prompt(SYSTEM_PROMPT_FILE)
        script_template = self._resources.load_prompt(SCRIPT_PROMPT_FILE)

        script_prompt = self._resources.render_template(
            script_template,
            {
                "TOPIC": request.topic,
                "STYLE_GUIDE": style_guide,
            },
        )

        full_prompt = f"{system_prompt}\n\n---\n\n{script_prompt}"

        markdown = self._llm.generate(full_prompt)

        result = ScriptResult(
            topic=request.topic,
            script_markdown=markdown,
            word_count=len(markdown.split()),
            generation_time_ms=(perf_counter() - started_at) * 1000,
        )

        logger.info(
            "Script generation completed (%d words)",
            result.word_count,
        )

        return result
