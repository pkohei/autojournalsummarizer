import os
from datetime import datetime
from time import sleep

import pytz

from retriever import NaturePhotonicsRetriever
from sender import DiscordSender
from summary import summarize_abstract


def main():
    model = 'gpt-3.5-turbo'
    openai_api_key = os.environ['OPENAI_API_KEY']
    discord_url = os.environ['DISCORD_URL']

    now = datetime.now(tz=pytz.timezone('Asia/Tokyo'))
    retriever = NaturePhotonicsRetriever()
    recent_entries = retriever.fetch_recent_entries(now, hours_ago=240)

    sender = DiscordSender(discord_url)
    for entry in recent_entries:
        abstract = retriever.extract_abstract(entry)
        summary = summarize_abstract(abstract, openai_api_key, model)
        sender.send_summary(entry, summary)
        sleep(5)


if __name__ == '__main__':
    main()
