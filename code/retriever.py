import os
import time
from abc import ABCMeta, abstractmethod

import feedparser
import requests
from bs4 import BeautifulSoup


class JournalRetriever(metaclass=ABCMeta):
    RSS_URL = ""
    LAST_ENTRIES_LOG_FILE = ""

    def __init__(self) -> None:
        self.entries = []
        self.updated_entries = []

    def retrieve(self):
        last_entry_ids = self.get_last_entry_ids()

        feed = feedparser.parse(self.RSS_URL)
        self.entries = self.format_entries(feed)
        self.updated_entries = self.retrieve_updated_entries(last_entry_ids)

        for entry in self.updated_entries:
            abst = self.extract_abstract(entry)
            entry['abstract'] = abst
            time.sleep(1)

        return self.updated_entries

    def get_last_entry_ids(self):
        if os.path.isfile(self.LAST_ENTRIES_LOG_FILE):
            with open(self.LAST_ENTRIES_LOG_FILE, 'r', encoding='UTF-8') as f:
                last_entry_ids = f.readlines()
                last_entry_ids = [e.replace('\n', '') for e in last_entry_ids]
        else:
            last_entry_ids = []
        return last_entry_ids

    def retrieve_updated_entries(self, last_entry_ids):
        updated_entries = []
        for entry in self.entries:
            if not (entry['id'] in last_entry_ids):
                updated_entries.append(entry)
        updated_entries.sort(key=lambda x: x['updated'])
        return updated_entries

    def update_log(self):
        if len(self.updated_entries) == 0:
            return

        os.makedirs(os.path.dirname(self.LAST_ENTRIES_LOG_FILE), exist_ok=True)
        with open(self.LAST_ENTRIES_LOG_FILE, 'w', encoding='UTF-8') as f:
            f.writelines([entry['id'] + '\n' for entry in self.entries])

        print(f'\"{self.LAST_ENTRIES_LOG_FILE}\" is updated!')

    @abstractmethod
    def format_entries(self, feed):
        return []

    @abstractmethod
    def extract_abstract(self, entry):
        return ""


class NaturePhotonicsRetriever(JournalRetriever):
    RSS_URL = 'https://www.nature.com/nphoton.rss'
    LAST_ENTRIES_LOG_FILE = "./logs/nature_photonics_log.txt"

    def format_entries(self, feed):
        entries = []
        for entry in feed.entries:
            formatted_entry = construct_entry(
                id=entry.id,
                title=entry.title,
                authors=[author.name for author in entry.authors],
                updated_parsed=entry.updated_parsed,
                link=entry.link
            )
            entries.append(formatted_entry)
        return entries

    def extract_abstract(self, entry):
        response = requests.get(entry['link'])
        soup = BeautifulSoup(response.text, 'html.parser')

        abs1_content = soup.find(id='Abs1-content')

        article_content = soup.find(
            class_='c-article-section__content--standfirst')
        if article_content:
            article_content = article_content.find_all('p', recursive=False)[0]
        else:
            article_content = None

        article_teaser = soup.find(class_='article__teaser')
        if article_teaser:
            article_teaser = article_teaser.find_all('p', recursive=False)[0]
        else:
            article_teaser = None

        abst = ""
        if abs1_content is not None:
            abst += abs1_content.text + '\n'
        if article_content is not None:
            abst += article_content.text + '\n'
        if article_teaser is not None:
            abst += article_teaser.text + '\n'

        return abst


class LightScienceApplicationsRetriever(JournalRetriever):
    RSS_URL = 'https://www.nature.com/lsa.rss'
    LAST_ENTRIES_LOG_FILE = "./logs/light_science_applications_log.txt"

    def format_entries(self, feed):
        entries = []
        for entry in feed.entries:
            formatted_entry = construct_entry(
                id=entry.id,
                title=entry.title,
                authors=[author.name for author in entry.authors],
                updated_parsed=entry.updated_parsed,
                link=entry.link
            )
            entries.append(formatted_entry)
        return entries

    def extract_abstract(self, entry):
        response = requests.get(entry['link'])
        soup = BeautifulSoup(response.text, 'html.parser')

        abs1_content = soup.find(id='Abs1-content')

        abst = abs1_content.text + '\n' if abs1_content is not None else ''

        return abst


class ArxivPhysicsOpticsRetriever(JournalRetriever):
    RSS_URL = 'http://export.arxiv.org/rss/physics.optics'
    LAST_ENTRIES_LOG_FILE = './logs/arxiv_physics_optics_log.txt'

    def format_entries(self, feed):
        entries = []

        for entry in feed.entries:
            authors = entry.author
            authors = BeautifulSoup(authors, "html.parser").text.split(', ')
            abst = BeautifulSoup(entry.description, 'html.parser').text

            formatted_entry = construct_entry(
                id=entry.id,
                title=entry.title,
                authors=authors,
                updated_parsed=feed.updated_parsed,
                link=entry.link,
                abstract=abst
            )
            entries.append(formatted_entry)

        return entries

    def extract_abstract(self, entry):
        return entry['abstract']


def construct_entry(
        id: str,
        title: str,
        authors: list[str],
        updated_parsed: time.struct_time,
        link: str,
        abstract: str = ""):
    return {
        'id': id,
        'title': title,
        'authors': authors,
        'updated': updated_parsed,
        'link': link,
        'abstract': abstract
    }
