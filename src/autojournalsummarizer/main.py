import argparse
import json
import os
import re
from datetime import datetime, timedelta, timezone
from tempfile import TemporaryDirectory

import arxiv  # type: ignore
import arxiv  # type: ignore
import requests
from openai import OpenAI
from pydantic import BaseModel
from pydrive2.auth import GoogleAuth  # type: ignore
from pydrive2.drive import GoogleDrive  # type: ignore
from pydrive2.auth import GoogleAuth  # type: ignore
from pydrive2.drive import GoogleDrive  # type: ignore
from pypdf import PdfReader
from pyzotero.zotero import Zotero  # type: ignore

from .config import Settings, get_settings


class Paper(BaseModel):
    idx: int
    title: str
    reason: str


class Papers(BaseModel):
    papers: list[Paper]


class Keyword(BaseModel):
    keyword: str
    explanation: str


class PaperSummary(BaseModel):
    japanese_title: str
    summary: str
    merit: str
    method: str
    valid: str
    discussion: str
    keywords: list[Keyword]


class Paper(BaseModel):
    idx: int
    title: str
    reason: str


class Papers(BaseModel):
    papers: list[Paper]


class Keyword(BaseModel):
    keyword: str
    explanation: str


class PaperSummary(BaseModel):
    japanese_title: str
    summary: str
    merit: str
    method: str
    valid: str
    discussion: str
    keywords: list[Keyword]


def main(num_papers: int, model: str) -> None:
    settings = get_settings()
    settings.ensure_directories()
    settings.ensure_files()

    last_published = get_last_published_datetime(settings)
    start_datetime = None
    if last_published is not None:
        start_datetime = last_published + timedelta(minutes=1)
    papers = retrieve_recent_arxiv_papers(
        settings,
        start_datetime=start_datetime,
    )
    print("Updated papers:", len(papers))
    if len(papers) == 0:
        print("There are no updated papers.")
        send_discord(settings, "本日の新着論文はありません。")
        return

    interesting_papers = extract_interesting_papers(settings, papers, num_papers, model)
    interesting_titles = [p.title for p in interesting_papers]
    print("Interesting papers:", len(interesting_papers))

    send_discord(
        settings,
        f"新着論文：{len(papers)}本\n"
        + f"関心度の高い論文：{len(interesting_papers)}本",
    )

    for paper in papers:
        if paper.title not in interesting_titles:
            update_log(settings, paper.published)
            continue
        with TemporaryDirectory() as dirpath:
            pdf_path = paper.download_pdf(dirpath=dirpath)
            text = extract_text_from_pdf(pdf_path)
            summary = summarize_paper(settings, paper.title, text, model)
            message = make_message(paper=paper, summary=summary)
            print(message)

            send_discord(settings, message)
            upload_google_drive(settings, pdf_path)
            register_zotero(settings, paper, pdf_path)
            update_log(settings, paper.published)


def test(num_papers: int, model: str) -> None:
    print("Test mode")
    settings = get_settings()
    settings.ensure_directories()
    settings.ensure_files()

    papers = retrieve_recent_arxiv_papers(settings)
    print("Updated papers:", len(papers))
    if len(papers) == 0:
        print("There are no updated papers.")
        return

    interesting_papers = extract_interesting_papers(settings, papers, num_papers, model)
    print("Interesting papers:", len(interesting_papers))

    for paper in interesting_papers:
        with TemporaryDirectory() as dirpath:
            pdf_path = paper.download_pdf(dirpath=dirpath)
            text = extract_text_from_pdf(pdf_path)
            summary = summarize_paper(settings, paper.title, text, model)
            message = make_message(paper=paper, summary=summary)
            print(message)
        break


def get_last_published_datetime(settings: Settings) -> datetime | None:
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


def retrieve_recent_arxiv_papers(
    settings: Settings,
    start_datetime: datetime | None = None,
) -> list[arxiv.Result]:
    category = settings.arxiv_category
    if start_datetime is None:
        query = f"cat:{category}"
    else:
        start_datetime_str = start_datetime.strftime("%Y%m%d%H%M%S")
        start_datetime_str = start_datetime.strftime("%Y%m%d%H%M%S")
        now = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
        query = f"cat:{category} AND submittedDate:[{start_datetime_str} TO {now}]"
        query = f"cat:{category} AND submittedDate:[{start_datetime_str} TO {now}]"

    search = arxiv.Search(
        query=query,
        max_results=settings.arxiv_max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    client = arxiv.Client()
    papers = list(client.results(search))

    return papers[::-1]


def extract_interesting_papers(
    settings: Settings, papers: list[arxiv.Result], num_papers: int, model: str
) -> list[arxiv.Result]:
    if not (settings.keywords_file.exists() and settings.filter_prompt_file.exists()):
        return papers

    prompt = settings.filter_prompt_file.read_text()
    keywords = settings.keywords_file.read_text().splitlines()

    keyword_sentence = ""
    for k in keywords:
        keyword_sentence += "- " + k + "\n"

    prompt = prompt.replace("{keywords}", keyword_sentence)

    settings.validate_required_env_vars("filter")
    client = OpenAI(api_key=settings.openai_api_key)

    titles_sentence = ""
    for idx, p in enumerate(papers):
        titles_sentence += f"{idx}. {p.title}\n"
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
    if response is None:
        return papers[:num_papers]
    target_idxs = [int(p.idx) for p in response.papers]

    interesting_papers = []
    for idx in target_idxs:
        interesting_papers.append(papers[idx])

    return interesting_papers


def extract_text_from_pdf(pdf_path: str) -> str:
def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def summarize_paper(
    settings: Settings, title: str, text: str, model: str
) -> PaperSummary | None:
    summarize_prompt = settings.summarize_prompt_file.read_text()

    settings.validate_required_env_vars("summarize")
    client = OpenAI(api_key=settings.openai_api_key)

    res = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "user",
                "content": summarize_prompt + f"[タイトル]\n{title}\n[本文]\n{text}",
            },
        ],
        response_format=PaperSummary,
    )
    return res.choices[0].message.parsed


def make_message(paper: arxiv.Result, summary: PaperSummary | None) -> str:
    if summary is None:
        return f"# [{paper.title}]({paper.links[0].href})\n論文の要約に失敗しました。"

def make_message(paper: arxiv.Result, summary: PaperSummary | None) -> str:
    if summary is None:
        return f"# [{paper.title}]({paper.links[0].href})\n論文の要約に失敗しました。"

    message = (
        f"# [{summary.japanese_title}]({paper.links[0].href})\n"
        f"第一著者：{paper.authors[0].name}\n"
        f"日付：{paper.published.strftime('%Y-%m-%d %H:%M:%S')}\n"
        "## 一言で説明すると？\n"
        f"{summary.summary}\n"
        "## 先行研究と比べて何がすごい？\n"
        f"{summary.merit}\n"
        "## 技術や手法のキモは何？\n"
        f"{summary.method}\n"
        "## どうやって有効だと検証した？\n"
        f"{summary.valid}\n"
        "## 課題や議論はある？\n"
        f"{summary.discussion}\n"
        "## キーワード\n"
    )
    for keyword in summary.keywords:
        message += f"- {keyword.keyword}：{keyword.explanation}\n"
    return message


def send_discord(settings: Settings, message: str) -> None:
    if not settings.discord_webhook_url:
        print("DISCORD_WEBHOOK_URL not found, skipping Discord notification")
        return

    headers = {"Content-Type": "application/json"}
    data = {"content": message}
    requests.post(settings.discord_webhook_url, data=json.dumps(data), headers=headers)
    print("Send message")
    print("------------")
    print(message)
    print("------------")


def upload_google_drive(settings: Settings, pdf_path: str) -> None:
    gauth = GoogleAuth(str(settings.google_auth_settings_file))
    gauth.ServiceAuth()
    drive = GoogleDrive(gauth)
    query = f'title = "{settings.google_folder_name}"'
    folders = drive.ListFile({"q": query}).GetList()
    file = drive.CreateFile(
        {
            "title": os.path.basename(pdf_path),
            "parents": [{"id": folders[0]["id"]}],
        }
    )
    file.SetContentFile(pdf_path)
    file.Upload({"convert": False})
    print("Upload to google drive:", os.path.basename(pdf_path))


def register_zotero(settings: Settings, paper: arxiv.Result, pdf_path: str) -> None:
    if not settings.zotero_api_key or not settings.zotero_library_id:
        print("ZOTERO credentials not found, skipping Zotero registration")
        return

    zot = Zotero(
        library_id=settings.zotero_library_id,
        library_type="user",
        api_key=settings.zotero_api_key,
    )

    item = zot.item_template("preprint")
    item["title"] = paper.title
    item["creators"] = []
    for author in paper.authors:
        try:
            first_name, last_name = author.name.split(maxsplit=1)
        except ValueError:
            first_name = author.name
            last_name = ""
        item["creators"].append(
            {
                "creatorType": "author",
                "firstName": first_name,
                "lastName": last_name,
            }
        )
    item["abstractNote"] = paper.summary
    item["repository"] = "arxiv"
    item["archiveID"] = "arXiv:" + re.sub(r"v[0-9]+", "", paper.get_short_id())
    item["date"] = paper.published.strftime("%Y-%m-%d")
    item["DOI"] = paper.doi
    item["url"] = re.sub(r"v[0-9]+", "", paper.links[0].href)
    item["libraryCatalog"] = "arXiv.org"

    collections = zot.collections()
    for collection in collections:
        if collection["data"]["name"] == settings.zotero_collection_name:
            collection_id = collection["key"]
            break
    item["collections"] = [collection_id]

    response = zot.create_items([item])
    item_id = response["success"]["0"]

    pdf_filename = os.path.basename(pdf_path)
    attachment = zot.item_template("attachment", linkmode="linked_file")
    attachment["title"] = pdf_filename
    attachment["path"] = pdf_filename
    attachment["contentType"] = "application/pdf"
    zot.create_items([attachment], parentid=item_id)

    print("Register to Zotero:", paper.title)


def update_log(settings: Settings, published_datetime: datetime) -> None:
    settings.last_date_file.write_text(published_datetime.isoformat())
    print("Log is updated!:", published_datetime.isoformat())


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
