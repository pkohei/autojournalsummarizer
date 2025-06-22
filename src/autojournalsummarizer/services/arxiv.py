"""arXiv paper retrieval service."""

from datetime import datetime, timezone

import arxiv  # type: ignore

from ..config import Settings


class ArxivService:
    """Service for retrieving papers from arXiv."""

    def __init__(self, settings: Settings) -> None:
        """Initialize ArxivService with settings."""
        self.settings = settings

    def retrieve_recent_papers(
        self, start_datetime: datetime | None = None
    ) -> list[arxiv.Result]:
        """Retrieve recent papers from arXiv.

        Args:
            start_datetime: Optional start datetime for filtering papers.

        Returns:
            List of arXiv papers sorted by submission date (oldest first).
        """
        category = self.settings.arxiv_category

        if start_datetime is None:
            query = f"cat:{category}"
        else:
            start_datetime_str = start_datetime.strftime("%Y%m%d%H%M%S")
            now = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
            query = f"cat:{category} AND submittedDate:[{start_datetime_str} TO {now}]"

        search = arxiv.Search(
            query=query,
            max_results=self.settings.arxiv_max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )

        client = arxiv.Client()
        papers = list(client.results(search))

        return papers[::-1]  # Reverse to get oldest first
