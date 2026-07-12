"""Load prompts and knowledge files from disk."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ResourceLoader:
    """Reads markdown resources from prompts/ and knowledge/ directories."""

    def __init__(self, prompts_dir: Path, knowledge_dir: Path) -> None:
        self._prompts_dir = prompts_dir
        self._knowledge_dir = knowledge_dir

    def load_prompt(self, filename: str) -> str:
        """Load a prompt template from the prompts directory."""
        return self._read(self._prompts_dir / filename)

    def load_knowledge(self, filename: str) -> str:
        """Load a knowledge document from the knowledge directory."""
        return self._read(self._knowledge_dir / filename)

    @staticmethod
    def render_template(template: str, variables: dict[str, str]) -> str:
        """Replace {{KEY}} placeholders with supplied values."""
        rendered = template
        for key, value in variables.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", value)
        return rendered

    def _read(self, path: Path) -> str:
        try:
            content = path.read_text(encoding="utf-8").strip()
            logger.debug("Loaded resource: %s", path)
            return content
        except FileNotFoundError as exc:
            logger.error("Resource not found: %s", path)
            raise FileNotFoundError(f"Resource not found: {path}") from exc
        except OSError as exc:
            logger.error("Failed to read resource: %s", path)
            raise OSError(f"Failed to read resource: {path}") from exc
