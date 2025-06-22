"""External service integrations for Discord, Google Drive, and Zotero."""

import json
import os
import re

import arxiv  # type: ignore
import requests
from pydrive2.auth import GoogleAuth  # type: ignore
from pydrive2.drive import GoogleDrive  # type: ignore
from pyzotero.zotero import Zotero  # type: ignore

from ..config import Settings
from ..models import PaperSummary


class DiscordService:
    """Service for Discord webhook notifications."""

    def __init__(self, settings: Settings) -> None:
        """Initialize DiscordService with settings."""
        self.settings = settings

    def send_message(self, message: str) -> None:
        """Send a message to Discord via webhook.

        Args:
            message: Message content to send.
        """
        if not self.settings.discord_webhook_url:
            print("DISCORD_WEBHOOK_URL not found, skipping Discord notification")
            return

        headers = {"Content-Type": "application/json"}
        data = {"content": message}
        requests.post(
            self.settings.discord_webhook_url, data=json.dumps(data), headers=headers
        )
        print("Send message")
        print("------------")
        print(message)
        print("------------")

    def make_paper_message(
        self, paper: arxiv.Result, summary: PaperSummary | None
    ) -> str:
        """Create a formatted message for a paper summary.

        Args:
            paper: arXiv paper object.
            summary: Structured paper summary.

        Returns:
            Formatted message string for Discord.
        """
        if summary is None:
            return (
                f"# [{paper.title}]({paper.links[0].href})\n論文の要約に失敗しました。"
            )

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


class GoogleDriveService:
    """Service for Google Drive file uploads."""

    def __init__(self, settings: Settings) -> None:
        """Initialize GoogleDriveService with settings."""
        self.settings = settings

    def upload_pdf(self, pdf_path: str) -> None:
        """Upload a PDF file to Google Drive.

        Args:
            pdf_path: Path to the PDF file to upload.
        """
        gauth = GoogleAuth(str(self.settings.google_auth_settings_file))
        gauth.ServiceAuth()
        drive = GoogleDrive(gauth)

        query = f'title = "{self.settings.google_folder_name}"'
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


class ZoteroService:
    """Service for Zotero bibliography management."""

    def __init__(self, settings: Settings) -> None:
        """Initialize ZoteroService with settings."""
        self.settings = settings

    def register_paper(self, paper: arxiv.Result, pdf_path: str) -> None:
        """Register a paper in Zotero with PDF attachment.

        Args:
            paper: arXiv paper object.
            pdf_path: Path to the PDF file to attach.
        """
        if not self.settings.zotero_api_key or not self.settings.zotero_library_id:
            print("ZOTERO credentials not found, skipping Zotero registration")
            return

        zot = Zotero(
            library_id=self.settings.zotero_library_id,
            library_type="user",
            api_key=self.settings.zotero_api_key,
        )

        # Create preprint item
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

        # Find collection
        collections = zot.collections()
        collection_id = None
        for collection in collections:
            if collection["data"]["name"] == self.settings.zotero_collection_name:
                collection_id = collection["key"]
                break

        if collection_id:
            item["collections"] = [collection_id]

        # Create item
        response = zot.create_items([item])
        item_id = response["success"]["0"]

        # Add PDF attachment
        pdf_filename = os.path.basename(pdf_path)
        attachment = zot.item_template("attachment", linkmode="linked_file")
        attachment["title"] = pdf_filename
        attachment["path"] = pdf_filename
        attachment["contentType"] = "application/pdf"
        zot.create_items([attachment], parentid=item_id)

        print("Register to Zotero:", paper.title)
