"""Persist generated scripts to disk."""

import logging
import re
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class FileWriter:
    """Writes generated scripts to the outputs/scripts directory."""

    def __init__(self, output_dir: Path) -> None:
        self._scripts_dir = output_dir / "scripts"
        self._storyboards_dir = output_dir / "storyboards"

    def save_script(self, topic: str, content: str) -> Path:
        """Save script markdown and return the file path."""
        self._scripts_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}_{_slugify_topic(topic)}.md"
        filepath = self._scripts_dir / filename

        try:
            filepath.write_text(content, encoding="utf-8")
        except OSError as exc:
            logger.exception("Failed to write script to %s", filepath)
            raise OSError(f"Failed to save script: {filepath}") from exc

        logger.info("Script saved to %s", filepath)
        return filepath

    def save_storyboard(self, topic: str, content: str) -> Path:
        """Save storyboard markdown and return the file path."""
        self._storyboards_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}_{_slugify_topic(topic)}_storyboard.md"
        filepath = self._storyboards_dir / filename

        try:
            filepath.write_text(content, encoding="utf-8")
        except OSError as exc:
            logger.exception("Failed to write storyboard to %s", filepath)
            raise OSError(f"Failed to save storyboard: {filepath}") from exc

        logger.info("Storyboard saved to %s", filepath)
        return filepath


def _slugify_topic(topic: str) -> str:
    """Convert a topic string to a filesystem-safe slug."""
    slug = re.sub(r"[^\w\s-]", "", topic.lower())
    slug = re.sub(r"[\s-]+", "_", slug).strip("_")
    return slug[:60] or "script"
