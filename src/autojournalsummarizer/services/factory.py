"""Service factory for dependency injection and service management."""

import logging
from typing import Any, cast

from ..config import Settings
from .arxiv import ArxivService
from .integrations import DiscordService, GoogleDriveService, ZoteroService
from .openai_service import OpenAIService


class ServiceFactory:
    """Factory for creating and managing service instances."""

    def __init__(self, settings: Settings, logger: logging.Logger) -> None:
        """Initialize ServiceFactory.

        Args:
            settings: Application settings.
            logger: Logger instance.
        """
        self.settings = settings
        self.logger = logger
        self._services: dict[str, Any] = {}

    def get_arxiv_service(self) -> ArxivService:
        """Get ArxivService instance (singleton)."""
        if "arxiv" not in self._services:
            self.logger.info("Initializing ArxivService")
            self._services["arxiv"] = ArxivService(self.settings)
        return cast(ArxivService, self._services["arxiv"])

    def get_openai_service(self) -> OpenAIService:
        """Get OpenAIService instance (singleton)."""
        if "openai" not in self._services:
            self.logger.info("Initializing OpenAIService")
            self._services["openai"] = OpenAIService(self.settings)
        return cast(OpenAIService, self._services["openai"])

    def get_discord_service(self) -> DiscordService:
        """Get DiscordService instance (singleton)."""
        if "discord" not in self._services:
            self.logger.info("Initializing DiscordService")
            self._services["discord"] = DiscordService(self.settings)
        return cast(DiscordService, self._services["discord"])

    def get_gdrive_service(self) -> GoogleDriveService:
        """Get GoogleDriveService instance (singleton)."""
        if "gdrive" not in self._services:
            self.logger.info("Initializing GoogleDriveService")
            self._services["gdrive"] = GoogleDriveService(self.settings)
        return cast(GoogleDriveService, self._services["gdrive"])

    def get_zotero_service(self) -> ZoteroService:
        """Get ZoteroService instance (singleton)."""
        if "zotero" not in self._services:
            self.logger.info("Initializing ZoteroService")
            self._services["zotero"] = ZoteroService(self.settings)
        return cast(ZoteroService, self._services["zotero"])

    def get_all_services(self) -> dict[str, Any]:
        """Get all initialized services."""
        return {
            "arxiv": self.get_arxiv_service(),
            "openai": self.get_openai_service(),
            "discord": self.get_discord_service(),
            "gdrive": self.get_gdrive_service(),
            "zotero": self.get_zotero_service(),
        }
