"""Workflow orchestration service for paper processing pipeline."""

import logging
import time
from collections.abc import Callable
from datetime import timedelta
from tempfile import TemporaryDirectory
from typing import Any

import arxiv  # type: ignore

from ..config import Settings
from ..logging_config import log_with_context
from ..services.utils import (
    extract_text_from_pdf,
    get_last_published_datetime,
    update_log,
)
from .factory import ServiceFactory


class WorkflowError(Exception):
    """Base exception for workflow errors."""

    pass


class RetryableError(WorkflowError):
    """Error that can be retried."""

    pass


class NonRetryableError(WorkflowError):
    """Error that should not be retried."""

    pass


def retry_on_failure(max_retries: int = 3, delay: float = 1.0) -> Callable:
    """Decorator for retrying operations with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts.
        delay: Initial delay between retries in seconds.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except NonRetryableError:
                    # Don't retry non-retryable errors
                    raise
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        break

                    wait_time = delay * (2**attempt)  # Exponential backoff
                    time.sleep(wait_time)

            # All retries exhausted
            raise RetryableError(
                f"Failed after {max_retries} retries"
            ) from last_exception

        return wrapper

    return decorator


class WorkflowService:
    """Service for orchestrating the complete paper processing workflow."""

    def __init__(
        self,
        settings: Settings,
        service_factory: ServiceFactory,
        logger: logging.Logger,
    ) -> None:
        """Initialize WorkflowService.

        Args:
            settings: Application settings.
            service_factory: Factory for service instances.
            logger: Logger instance.
        """
        self.settings = settings
        self.factory = service_factory
        self.logger = logger

    def run_production_workflow(self, num_papers: int, model: str) -> None:
        """Run the complete production workflow.

        Args:
            num_papers: Maximum number of papers to process.
            model: OpenAI model to use.
        """
        try:
            log_with_context(
                self.logger,
                logging.INFO,
                "Starting production workflow",
                num_papers=num_papers,
                model=model,
            )

            self._ensure_setup()
            papers = self._retrieve_papers()

            if not papers:
                self._handle_no_papers()
                return

            interesting_papers = self._filter_papers(papers, num_papers, model)
            self._send_summary_notification(papers, interesting_papers)
            self._process_interesting_papers(papers, interesting_papers, model)

            log_with_context(
                self.logger,
                logging.INFO,
                "Production workflow completed successfully",
                total_papers=len(papers),
                interesting_papers=len(interesting_papers),
            )

        except Exception as e:
            log_with_context(
                self.logger, logging.ERROR, "Production workflow failed", error=str(e)
            )
            raise

    def run_test_workflow(self, num_papers: int, model: str) -> None:
        """Run the test workflow (no external notifications/uploads).

        Args:
            num_papers: Maximum number of papers to process.
            model: OpenAI model to use.
        """
        try:
            log_with_context(
                self.logger,
                logging.INFO,
                "Starting test workflow",
                num_papers=num_papers,
                model=model,
            )

            self._ensure_setup()
            papers = self._retrieve_papers()

            if not papers:
                self.logger.info("No papers found for testing")
                return

            interesting_papers = self._filter_papers(papers, num_papers, model)

            # Process only the first interesting paper in test mode
            if interesting_papers:
                self._process_single_paper_for_test(interesting_papers[0], model)

            log_with_context(
                self.logger,
                logging.INFO,
                "Test workflow completed successfully",
                total_papers=len(papers),
                interesting_papers=len(interesting_papers),
            )

        except Exception as e:
            log_with_context(
                self.logger, logging.ERROR, "Test workflow failed", error=str(e)
            )
            raise

    def _ensure_setup(self) -> None:
        """Ensure directories and files are properly set up."""
        try:
            self.settings.ensure_directories()
            self.settings.ensure_files()
            self.logger.info("Setup completed successfully")
        except Exception as e:
            raise NonRetryableError(f"Setup failed: {e}") from e

    @retry_on_failure(max_retries=3, delay=2.0)
    def _retrieve_papers(self) -> list[arxiv.Result]:
        """Retrieve recent papers from arXiv with retry logic."""
        try:
            arxiv_service = self.factory.get_arxiv_service()

            last_published = get_last_published_datetime(self.settings)
            start_datetime = None
            if last_published is not None:
                start_datetime = last_published + timedelta(minutes=1)

            papers = arxiv_service.retrieve_recent_papers(start_datetime=start_datetime)

            log_with_context(
                self.logger,
                logging.INFO,
                "Papers retrieved successfully",
                count=len(papers),
            )

            return papers

        except Exception as e:
            log_with_context(
                self.logger, logging.WARNING, "Failed to retrieve papers", error=str(e)
            )
            raise RetryableError(f"Paper retrieval failed: {e}") from e

    def _handle_no_papers(self) -> None:
        """Handle the case when no new papers are found."""
        self.logger.info("No new papers found")
        discord_service = self.factory.get_discord_service()
        discord_service.send_message("本日の新着論文はありません。")

    @retry_on_failure(max_retries=2, delay=1.0)
    def _filter_papers(
        self, papers: list[arxiv.Result], num_papers: int, model: str
    ) -> list[arxiv.Result]:
        """Filter papers based on keywords using OpenAI."""
        try:
            openai_service = self.factory.get_openai_service()
            interesting_papers = openai_service.filter_interesting_papers(
                papers, num_papers, model
            )

            log_with_context(
                self.logger,
                logging.INFO,
                "Papers filtered successfully",
                total=len(papers),
                interesting=len(interesting_papers),
            )

            return interesting_papers

        except Exception as e:
            log_with_context(
                self.logger, logging.WARNING, "Failed to filter papers", error=str(e)
            )
            raise RetryableError(f"Paper filtering failed: {e}") from e

    def _send_summary_notification(
        self, papers: list[arxiv.Result], interesting_papers: list[arxiv.Result]
    ) -> None:
        """Send summary notification to Discord."""
        try:
            discord_service = self.factory.get_discord_service()
            message = (
                f"新着論文：{len(papers)}本\n"
                f"関心度の高い論文：{len(interesting_papers)}本"
            )
            discord_service.send_message(message)

            self.logger.info("Summary notification sent successfully")

        except Exception as e:
            log_with_context(
                self.logger,
                logging.WARNING,
                "Failed to send summary notification",
                error=str(e),
            )
            # Don't raise - this is not critical

    def _process_interesting_papers(
        self,
        all_papers: list[arxiv.Result],
        interesting_papers: list[arxiv.Result],
        model: str,
    ) -> None:
        """Process all interesting papers."""
        interesting_titles = {p.title for p in interesting_papers}

        for paper in all_papers:
            if paper.title not in interesting_titles:
                update_log(self.settings, paper.published)
                continue

            try:
                self._process_single_paper(paper, model)
            except Exception as e:
                log_with_context(
                    self.logger,
                    logging.ERROR,
                    "Failed to process paper",
                    paper_title=paper.title,
                    error=str(e),
                )
                # Continue with next paper rather than failing entire workflow
                update_log(self.settings, paper.published)

    def _process_single_paper(self, paper: arxiv.Result, model: str) -> None:
        """Process a single paper through the complete pipeline."""
        with TemporaryDirectory() as dirpath:
            try:
                # Download and extract text
                pdf_path = paper.download_pdf(dirpath=dirpath)
                text = extract_text_from_pdf(pdf_path)

                # Generate summary
                openai_service = self.factory.get_openai_service()
                summary = openai_service.summarize_paper(paper.title, text, model)

                # Create and send message
                discord_service = self.factory.get_discord_service()
                message = discord_service.make_paper_message(
                    paper=paper, summary=summary
                )
                discord_service.send_message(message)

                # Upload to external services
                gdrive_service = self.factory.get_gdrive_service()
                gdrive_service.upload_pdf(pdf_path)

                zotero_service = self.factory.get_zotero_service()
                zotero_service.register_paper(paper, pdf_path)

                # Update log
                update_log(self.settings, paper.published)

                log_with_context(
                    self.logger,
                    logging.INFO,
                    "Paper processed successfully",
                    paper_title=paper.title,
                )

            except Exception as e:
                log_with_context(
                    self.logger,
                    logging.ERROR,
                    "Paper processing failed",
                    paper_title=paper.title,
                    error=str(e),
                )
                raise

    def _process_single_paper_for_test(self, paper: arxiv.Result, model: str) -> None:
        """Process a single paper for testing (no external uploads)."""
        with TemporaryDirectory() as dirpath:
            try:
                # Download and extract text
                pdf_path = paper.download_pdf(dirpath=dirpath)
                text = extract_text_from_pdf(pdf_path)

                # Generate summary
                openai_service = self.factory.get_openai_service()
                summary = openai_service.summarize_paper(paper.title, text, model)

                # Create message (but don't send)
                discord_service = self.factory.get_discord_service()
                message = discord_service.make_paper_message(
                    paper=paper, summary=summary
                )

                print(message)  # Print instead of sending

                log_with_context(
                    self.logger,
                    logging.INFO,
                    "Test paper processed successfully",
                    paper_title=paper.title,
                )

            except Exception as e:
                log_with_context(
                    self.logger,
                    logging.ERROR,
                    "Test paper processing failed",
                    paper_title=paper.title,
                    error=str(e),
                )
                raise
