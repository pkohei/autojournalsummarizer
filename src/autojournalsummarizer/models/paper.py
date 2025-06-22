"""Paper-related data models for structured data handling."""

from pydantic import BaseModel, Field


class Paper(BaseModel):
    """Represents a filtered paper from arXiv search results."""

    idx: int = Field(description="Index of the paper in the original search results")
    title: str = Field(description="Title of the paper")
    reason: str = Field(description="Reason why this paper was selected as interesting")


class Papers(BaseModel):
    """Collection of filtered papers."""

    papers: list[Paper] = Field(description="List of interesting papers")


class Keyword(BaseModel):
    """Represents a keyword with its explanation."""

    keyword: str = Field(description="The keyword term")
    explanation: str = Field(description="Explanation of the keyword in Japanese")


class PaperSummary(BaseModel):
    """Structured summary of a research paper in Japanese."""

    japanese_title: str = Field(description="Japanese translation of the paper title")
    summary: str = Field(description="Brief summary in Japanese")
    merit: str = Field(
        description="What makes this paper superior to previous research"
    )
    method: str = Field(description="Key technical methods or approaches used")
    valid: str = Field(description="How the effectiveness was validated")
    discussion: str = Field(description="Limitations, challenges, or future work")
    keywords: list[Keyword] = Field(description="Key technical terms with explanations")
