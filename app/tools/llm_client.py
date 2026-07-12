"""LLM provider interface and Ollama implementation."""

import logging
from typing import Protocol

from ollama import Client

from app.config.settings import Settings

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when the LLM provider fails to generate a response."""


class LLMProvider(Protocol):
    """Contract for any LLM backend. Swap implementations in this module only."""

    def generate(self, prompt: str) -> str:
        """Send a prompt and return the generated text."""
        ...


class LLMClient:
    """Ollama-backed implementation of LLMProvider."""

    def __init__(self, settings: Settings) -> None:
        self._client = Client(host=settings.ollama_host)
        self._model = settings.ollama_model

    def generate(self, prompt: str) -> str:
        """Send a prompt to Ollama and return the response text."""
        logger.info("Requesting generation from model: %s", self._model)
        try:
            response = self._client.chat(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:
            logger.exception("Ollama request failed")
            raise LLMError(
                f"LLM request failed. Ensure Ollama is running and "
                f"model '{self._model}' is available."
            ) from exc

        content = response.message.content
        if not content:
            logger.error("Ollama returned an empty response")
            raise LLMError("LLM returned an empty response.")

        logger.info("Generation complete (%d characters)", len(content))
        return content.strip()
