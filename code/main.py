import os
from datetime import datetime
from time import sleep

import pytz

import retriever
from sender import DiscordSender
from summary import summarize_abstract


def main():
    model = 'gpt-3.5-turbo'
    openai_api_key = os.environ['OPENAI_API_KEY']
    discord_url = os.environ['DISCORD_URL']

    now = datetime.now(tz=pytz.timezone('Asia/Tokyo'))

    retrievers = [
        retriever.NaturePhotonicsRetriever(),
        retriever.LightScienceApplicationsRetriever(),
        retriever.ArxivPhysicsOpticsRetriever(),
    ]

    print('try to fetch recent entries...')
    recent_entries = []
    for ret in retrievers:
        recent_entries += ret.fetch_recent_entries(now, hours_ago=24)
    print(f'{len(recent_entries)} entries are fetched!')

    sender = DiscordSender(discord_url)
    for entry in recent_entries:
        if entry['abstract']:
            summary = summarize_abstract(
                entry['abstract'],
                openai_api_key,
                model)
        else:
            summary = ""
        sender.send_summary(entry, summary)
        sleep(1)


if __name__ == '__main__':
    main()
