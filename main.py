import json
import os
import re
import requests
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from tempfile import TemporaryDirectory

import arxiv
from openai import OpenAI
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pypdf import PdfReader
from pyzotero.zotero import Zotero

MODEL = "gpt-4o"
ARXIV_CATEGORY = "cs.LG"

FILTER_PROMPT_FILE = "./prompts/filter_prompt.txt"
LAST_DATE_FILE = "./settings/last_date.txt"
KEYWORDS_FILE = "./settings/keywords.txt"

SUMMARIZE_PROMPT_FILE = "./prompts/summarize_prompt.txt"

GOOGLE_AUTH_SETTING_FILE = "./settings/auth_settings.yaml"
GOOGLE_FOLDER_NAME = "papers"

ZOTERO_COLLECTION_NAME = "daily"


def main() -> None:
    last_published = get_last_published_datetime()
    papers = retrieve_recent_arxiv_papers(
        category=ARXIV_CATEGORY,
        start_datetime=last_published + timedelta(minutes=1),
    )
    print("Updated papers:", len(papers))
    if len(papers) == 0:
        print("There are no updated papers.")
        return

    interesting_papers = extract_interesting_papers(papers)
    interesting_titles = [p.title for p in interesting_papers]
    print("Interesting papers:", len(interesting_papers))

    send_discord(
        f"新着論文：{len(papers)}本\n"
        f"関心度の高い論文：{len(interesting_papers)}本"
    )

    clear_log()
    for paper in papers:
        if paper.title not in interesting_titles:
            update_log(paper.published)
            continue
        with TemporaryDirectory() as dirpath:
            pdf_path = paper.download_pdf(dirpath=dirpath)
            text = extract_text_from_pdf(pdf_path)
            summary = summarize_paper(paper.title, text)
            message = make_message(paper=paper, summary=summary)

            send_discord(message)
            upload_google_drive(pdf_path)
            register_zotero(paper, pdf_path)
            update_log(paper.published)


def get_last_published_datetime() -> Union[datetime, None]:
    if not os.path.exists(LAST_DATE_FILE):
        with open(LAST_DATE_FILE, mode="w") as f:
            f.write("")
        return
    with open(LAST_DATE_FILE, mode="r") as f:
        last_published = f.read()
        if last_published == "":
            return
        last_published = datetime.fromisoformat(last_published)
    return last_published


def retrieve_recent_arxiv_papers(
    category: str,
    start_datetime: Optional[datetime] = None,
) -> list[arxiv.Result]:
    if start_datetime is None:
        query = f"cat:{category}"
    else:
        start_datetime = start_datetime.strftime("%Y%m%d%H%M%S")
        now = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
        query = f"cat:{category} AND submittedDate:[{start_datetime} TO {now}]"

    search = arxiv.Search(
        query=query,
        max_results=300,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    client = arxiv.Client()
    papers = list(client.results(search))

    return papers[::-1]


def extract_interesting_papers(papers: list[arxiv.Result]):
    if not (os.path.exists(KEYWORDS_FILE) and os.path.exists(FILTER_PROMPT_FILE)):
        return papers

    with open(FILTER_PROMPT_FILE, mode="r") as f:
        prompt = f.read()

    with open(KEYWORDS_FILE, mode="r") as f:
        keywords = f.readlines()

    keyword_sentence = ""
    for k in keywords:
        keyword_sentence += "- " + k

    prompt = prompt.replace("{keywords}", keyword_sentence)

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    titles_sentence = ""
    for idx, p in enumerate(papers):
        titles_sentence += f"{idx}. {p.title}\n"
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": titles_sentence},
        ],
        response_format={"type": "json_object"},
    )
    response = json.loads(completion.choices[0].message.content)
    print(response)
    target_idxs = [int(p["idx"]) for p in response["papers"]]

    interesting_papers = []
    for idx in target_idxs:
        interesting_papers.append(papers[idx])

    return interesting_papers


def extract_text_from_pdf(pdf_path: str):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def summarize_paper(title: str, text: str) -> dict[str, str]:
    with open(SUMMARIZE_PROMPT_FILE, mode="r") as f:
        summarize_prompt = f.read()

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": summarize_prompt},
            {
                "role": "user",
                "content": f"[タイトル]\n{title}\n[本文]\n{text}",
            },
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(res.choices[0].message.content)


def make_message(paper: arxiv.Result, summary: dict[str, str]) -> str:
    message = (
        f"# [{summary['japanese_title']}]({paper.links[0].href})\n"
        f"第一著者：{paper.authors[0].name}\n"
        f"日付：{paper.published.strftime('%Y-%m-%d %H:%M:%S')}\n"
        "## 一言で説明すると？\n"
        f"{summary['summary']}\n"
        "## 先行研究と比べて何がすごい？\n"
        f"{summary['merit']}\n"
        "## 技術や手法のキモは何？\n"
        f"{summary['method']}\n"
        "## どうやって有効だと検証した？\n"
        f"{summary['valid']}\n"
        "## 課題や議論はある？\n"
        f"{summary['discussion']}\n"
    )
    return message


def send_discord(message: str) -> None:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    headers = {"Content-Type": "application/json"}
    data = {"content": message}
    requests.post(webhook_url, data=json.dumps(data), headers=headers)
    print("Send message")
    print("------------")
    print(message)
    print("------------")


def upload_google_drive(pdf_path: str) -> None:
    gauth = GoogleAuth(GOOGLE_AUTH_SETTING_FILE)
    gauth.ServiceAuth()
    drive = GoogleDrive(gauth)
    folders = drive.ListFile({"q": f'title = "{GOOGLE_FOLDER_NAME}"'}).GetList()
    file = drive.CreateFile(
        {
            "title": os.path.basename(pdf_path),
            "parents": [{"id": folders[0]["id"]}],
        }
    )
    file.SetContentFile(pdf_path)
    file.Upload({"convert": False})
    print("Upload to google drive:", os.path.basename(pdf_path))


def register_zotero(paper: arxiv.Result, pdf_path: str) -> None:
    zot = Zotero(
        library_id=os.environ.get("ZOTERO_LIBRARY_ID"),
        library_type="user",
        api_key=os.environ.get("ZOTERO_API_KEY"),
    )

    item = zot.item_template("preprint")
    item["title"] = paper.title
    item["creators"] = []
    for author in paper.authors:
        first_name, last_name = author.name.split(maxsplit=1)
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
        if collection["data"]["name"] == ZOTERO_COLLECTION_NAME:
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


def clear_log() -> None:
    with open(LAST_DATE_FILE, mode="w") as f:
        f.write("")
    print("Log is cleared!")


def update_log(published_datetime: datetime) -> None:
    with open(LAST_DATE_FILE, mode="w") as f:
        f.write(published_datetime.isoformat())
    print("Log is updated!:", published_datetime.isoformat())


if __name__ == "__main__":
    main()
