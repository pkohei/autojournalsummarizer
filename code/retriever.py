from datetime import datetime, timedelta
from time import mktime

import feedparser
import pytz
import requests
from bs4 import BeautifulSoup


class NaturePhotonicsRetriever:
    rss_url = 'https://www.nature.com/nphoton.rss'

    def fetch_recent_entries(self, now=None, hours_ago=24):
        feed = feedparser.parse(self.rss_url)
        entries = feed.entries
        recent_entries = retrieve_recent_entries(
            entries, now=now, hours_ago=hours_ago)
        return recent_entries

    def extract_abstract(self, entry):
        response = requests.get(entry.link)
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


def check_entry_recent(entry, now=None, hours_ago=24):
    jst = pytz.timezone('Asia/Tokyo')

    if now is None:
        now = datetime.now(tz=jst)

    entry_time = datetime.fromtimestamp(mktime(entry.updated_parsed), tz=jst)
    start_time = now - timedelta(hours=hours_ago)

    if (start_time <= entry_time < now):
        return True

    return False


def retrieve_recent_entries(entries, now=None, hours_ago=24):
    if now is None:
        now = datetime.now(tz=pytz.timezone('Asia/Tokyo'))

    recent_entries = []

    for entry in entries:
        if (check_entry_recent(entry, now, hours_ago)):
            recent_entries.append(entry)

    return recent_entries
