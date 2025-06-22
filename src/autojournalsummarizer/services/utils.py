"""Utility functions for file operations and data management."""

from datetime import datetime

from pypdf import PdfReader

from ..config import Settings


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text content as a string.
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def get_last_published_datetime(settings: Settings) -> datetime | None:
    """Get the last processed paper timestamp from file.

    Args:
        settings: Application settings.

    Returns:
        Last published datetime or None if no timestamp exists.
    """
    last_date_file = settings.last_date_file
    if not last_date_file.exists():
        last_date_file.write_text("")
        return None

    last_published = last_date_file.read_text().strip()
    print(last_published)
    if last_published == "":
        return None

    last_published_dt = datetime.fromisoformat(last_published)
    return last_published_dt


def update_log(settings: Settings, published_datetime: datetime) -> None:
    """Update the last processed paper timestamp.

    Args:
        settings: Application settings.
        published_datetime: DateTime to record as last processed.
    """
    settings.last_date_file.write_text(published_datetime.isoformat())
    print("Log is updated!:", published_datetime.isoformat())
