"""ScriptWriter agent — loads prompts, calls the LLM, returns markdown."""

import logging
from typing import Protocol

from app.models.script import ScriptRequest
from app.tools.llm_client import LLMProvider
from app.tools.resource_loader import ResourceLoader

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_FILE = "system_prompt.md"
SCRIPT_PROMPT_FILE = "script_prompt.md"


class ScriptGenerator(Protocol):
    """Contract for agents that produce script markdown from a topic."""

    def generate(self, request: ScriptRequest, style_guide: str) -> str:
        """Generate a markdown script for the given request and style guide."""
        ...


class ScriptWriterAgent:
    """Generates a YouTube script by composing prompts and calling the LLM."""

    def __init__(self, llm: LLMProvider, resource_loader: ResourceLoader) -> None:
        self._llm = llm
        self._resources = resource_loader

    def generate(self, request: ScriptRequest, style_guide: str) -> str:
        """Build the full prompt, call the LLM, and return markdown script only."""
        logger.info("Generating script for topic: %s", request.topic)

        system_prompt = self._resources.load_prompt(SYSTEM_PROMPT_FILE)
        script_template = self._resources.load_prompt(SCRIPT_PROMPT_FILE)

        script_prompt = self._resources.render_template(
            script_template,
            {"TOPIC": request.topic, "STYLE_GUIDE": style_guide},
        )

        full_prompt = f"{system_prompt}\n\n---\n\n{script_prompt}"
        return self._llm.generate(full_prompt)
