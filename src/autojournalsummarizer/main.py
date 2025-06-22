import argparse
from datetime import timedelta
from tempfile import TemporaryDirectory

from .config import get_settings
from .services import (
    ArxivService,
    DiscordService,
    GoogleDriveService,
    OpenAIService,
    ZoteroService,
    extract_text_from_pdf,
    get_last_published_datetime,
    update_log,
)


def main(num_papers: int, model: str) -> None:
    settings = get_settings()
    settings.ensure_directories()
    settings.ensure_files()

    # Initialize services
    arxiv_service = ArxivService(settings)
    openai_service = OpenAIService(settings)
    discord_service = DiscordService(settings)
    gdrive_service = GoogleDriveService(settings)
    zotero_service = ZoteroService(settings)

    last_published = get_last_published_datetime(settings)
    start_datetime = None
    if last_published is not None:
        start_datetime = last_published + timedelta(minutes=1)

    papers = arxiv_service.retrieve_recent_papers(start_datetime=start_datetime)
    print("Updated papers:", len(papers))
    if len(papers) == 0:
        print("There are no updated papers.")
        discord_service.send_message("本日の新着論文はありません。")
        return

    interesting_papers = openai_service.filter_interesting_papers(
        papers, num_papers, model
    )
    interesting_titles = [p.title for p in interesting_papers]
    print("Interesting papers:", len(interesting_papers))

    discord_service.send_message(
        f"新着論文：{len(papers)}本\n"
        + f"関心度の高い論文：{len(interesting_papers)}本"
    )

    for paper in papers:
        if paper.title not in interesting_titles:
            update_log(settings, paper.published)
            continue
        with TemporaryDirectory() as dirpath:
            pdf_path = paper.download_pdf(dirpath=dirpath)
            text = extract_text_from_pdf(pdf_path)
            summary = openai_service.summarize_paper(paper.title, text, model)
            message = discord_service.make_paper_message(paper=paper, summary=summary)
            print(message)

            discord_service.send_message(message)
            gdrive_service.upload_pdf(pdf_path)
            zotero_service.register_paper(paper, pdf_path)
            update_log(settings, paper.published)


def test(num_papers: int, model: str) -> None:
    print("Test mode")
    settings = get_settings()
    settings.ensure_directories()
    settings.ensure_files()

    # Initialize services
    arxiv_service = ArxivService(settings)
    openai_service = OpenAIService(settings)
    discord_service = DiscordService(settings)

    papers = arxiv_service.retrieve_recent_papers()
    print("Updated papers:", len(papers))
    if len(papers) == 0:
        print("There are no updated papers.")
        return

    interesting_papers = openai_service.filter_interesting_papers(
        papers, num_papers, model
    )
    print("Interesting papers:", len(interesting_papers))

    for paper in interesting_papers:
        with TemporaryDirectory() as dirpath:
            pdf_path = paper.download_pdf(dirpath=dirpath)
            text = extract_text_from_pdf(pdf_path)
            summary = openai_service.summarize_paper(paper.title, text, model)
            message = discord_service.make_paper_message(paper=paper, summary=summary)
            print(message)
        break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_papers", type=int, default=20)
    parser.add_argument("--model", type=str, default="gpt-4o")
    parser.add_argument("--test", action="store_true", default=False)
    args = parser.parse_args()
    num_papers = args.num_papers
    model = args.model

    if args.test:
        test(num_papers, model)
    else:
        main(num_papers, model)
