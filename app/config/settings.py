"""Application settings loaded from environment variables."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseModel):
    """Runtime configuration for the application."""

    app_name: str = Field(default="THNKBYD AI Studio", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    ollama_host: str = Field(default="http://localhost:11434", alias="OLLAMA_HOST")
    ollama_model: str = Field(default="qwen2.5:3b", alias="OLLAMA_MODEL")
    output_dir: Path = Field(default=PROJECT_ROOT / "outputs", alias="OUTPUT_DIR")
    huggingface_api_key: str = Field(default="", alias="HUGGINGFACE_API_KEY")
    huggingface_image_model: str = Field(
        default="stabilityai/stable-diffusion-xl-base-1.0",
        alias="HUGGINGFACE_IMAGE_MODEL",
    )
    model_config = {"populate_by_name": True}

    @property
    def prompts_dir(self) -> Path:
        """Directory containing prompt templates."""
        return PROJECT_ROOT / "app" / "prompts"

    @property
    def knowledge_dir(self) -> Path:
        """Directory containing knowledge and style documents."""
        return PROJECT_ROOT / "app" / "knowledge"


def get_settings() -> Settings:
    """Return application settings from environment variables."""
    import os

    return Settings(
        APP_NAME=os.getenv("APP_NAME", "THNKBYD AI Studio"),
        APP_ENV=os.getenv("APP_ENV", "development"),
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
        OLLAMA_HOST=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        OLLAMA_MODEL=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
        OUTPUT_DIR=_resolve_output_dir(os.getenv("OUTPUT_DIR", "outputs")),
        HUGGINGFACE_API_KEY=os.getenv("HUGGINGFACE_API_KEY", ""),
        HUGGINGFACE_IMAGE_MODEL=os.getenv(
            "HUGGINGFACE_IMAGE_MODEL", "black-forest-labs/FLUX.1-dev"
        ),
    )


def _resolve_output_dir(value: str) -> Path:
    """Resolve output directory relative to project root when needed."""
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path
