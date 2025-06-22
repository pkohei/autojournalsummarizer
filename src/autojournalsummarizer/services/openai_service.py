"""OpenAI API service for paper filtering and summarization."""

import arxiv  # type: ignore
from openai import OpenAI

from ..config import Settings
from ..models import Papers, PaperSummary


class OpenAIService:
    """Service for OpenAI API operations."""

    def __init__(self, settings: Settings) -> None:
        """Initialize OpenAIService with settings."""
        self.settings = settings

    def filter_interesting_papers(
        self, papers: list[arxiv.Result], num_papers: int, model: str
    ) -> list[arxiv.Result]:
        """Filter papers based on user-defined keywords using OpenAI.

        Args:
            papers: List of arXiv papers to filter.
            num_papers: Maximum number of papers to return if filtering fails.
            model: OpenAI model to use for filtering.

        Returns:
            List of interesting papers based on keyword matching.
        """
        if not (
            self.settings.keywords_file.exists()
            and self.settings.filter_prompt_file.exists()
        ):
            return papers

        prompt = self.settings.filter_prompt_file.read_text()
        keywords = self.settings.keywords_file.read_text().splitlines()

        keyword_sentence = ""
        for keyword in keywords:
            keyword_sentence += "- " + keyword + "\n"

        prompt = prompt.replace("{keywords}", keyword_sentence)

        self.settings.validate_required_env_vars("filter")
        client = OpenAI(api_key=self.settings.openai_api_key)

        titles_sentence = ""
        for idx, paper in enumerate(papers):
            titles_sentence += f"{idx}. {paper.title}\n"

        completion = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "user", "content": prompt + titles_sentence},
            ],
            response_format=Papers,
        )

        response = completion.choices[0].message.parsed
        print(response)

        if response is None:
            return papers[:num_papers]

        target_idxs = [int(paper.idx) for paper in response.papers]

        interesting_papers = []
        for idx in target_idxs:
            interesting_papers.append(papers[idx])

        return interesting_papers

    def summarize_paper(self, title: str, text: str, model: str) -> PaperSummary | None:
        """Generate a structured summary of a research paper.

        Args:
            title: Paper title.
            text: Full text content of the paper.
            model: OpenAI model to use for summarization.

        Returns:
            Structured paper summary or None if summarization fails.
        """
        summarize_prompt = self.settings.summarize_prompt_file.read_text()

        self.settings.validate_required_env_vars("summarize")
        client = OpenAI(api_key=self.settings.openai_api_key)

        response = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": summarize_prompt
                    + f"[タイトル]\n{title}\n[本文]\n{text}",
                },
            ],
            response_format=PaperSummary,
        )

        return response.choices[0].message.parsed
