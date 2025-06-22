"""Application settings and configuration management."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ArXiv settings
    arxiv_category: str = Field(default="cs.LG", description="ArXiv category to search")
    arxiv_max_results: int = Field(default=50, description="Maximum papers to retrieve")

    # OpenAI settings
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    default_model: str = Field(default="gpt-4o", description="Default OpenAI model")

    # Discord settings
    discord_webhook_url: str | None = Field(
        default=None, description="Discord webhook URL for notifications"
    )

    # Zotero settings
    zotero_api_key: str | None = Field(default=None, description="Zotero API key")
    zotero_library_id: str | None = Field(default=None, description="Zotero library ID")
    zotero_collection_name: str = Field(
        default="daily", description="Zotero collection name"
    )

    # Google Drive settings
    google_folder_name: str = Field(
        default="papers", description="Google Drive folder name"
    )

    # File paths
    base_dir: Path = Field(
        default_factory=lambda: Path.cwd(), description="Base directory"
    )

    @property
    def filter_prompt_file(self) -> Path:
        """Path to filter prompt file."""
        return self.base_dir / "prompts" / "filter_prompt.txt"

    @property
    def summarize_prompt_file(self) -> Path:
        """Path to summarize prompt file."""
        return self.base_dir / "prompts" / "summarize_prompt.txt"

    @property
    def last_date_file(self) -> Path:
        """Path to last date tracking file."""
        return self.base_dir / "settings" / "last_date.txt"

    @property
    def keywords_file(self) -> Path:
        """Path to keywords file."""
        return self.base_dir / "settings" / "keywords.txt"

    @property
    def google_auth_settings_file(self) -> Path:
        """Path to Google auth settings file."""
        return self.base_dir / "settings" / "auth_settings.yaml"

    def validate_required_env_vars(self, operation: str) -> None:
        """Validate required environment variables for specific operations."""
        if operation in ("filter", "summarize") and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        if operation == "notify" and not self.discord_webhook_url:
            raise ValueError("DISCORD_WEBHOOK_URL environment variable not set")

        if operation == "zotero" and (
            not self.zotero_api_key or not self.zotero_library_id
        ):
            raise ValueError(
                "ZOTERO_API_KEY and ZOTERO_LIBRARY_ID environment variables not set"
            )

    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        directories = [
            self.base_dir / "prompts",
            self.base_dir / "settings",
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def ensure_files(self) -> None:
        """Ensure required files exist."""
        # Create last_date.txt if it doesn't exist
        if not self.last_date_file.exists():
            self.last_date_file.touch()


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
