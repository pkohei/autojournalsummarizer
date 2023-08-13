import os
from time import sleep

import retriever
from sender import DiscordSender
from summary import summarize_abstract


def main():
    model = 'gpt-3.5-turbo'
    openai_api_key = os.environ['OPENAI_API_KEY']
    discord_url = os.environ['DISCORD_URL']

    retrievers = [
        retriever.NaturePhotonicsRetriever(),
        retriever.LightScienceApplicationsRetriever(),
        retriever.ArxivPhysicsOpticsRetriever(),
    ]

    print('try to fetch updated entries...')
    updated_entries = []
    for ret in retrievers:
        updated_entries += ret.retrieve()
    print(f'{len(updated_entries)} entries are fetched!')

    sender = DiscordSender(discord_url)
    for entry in updated_entries:
        if entry['abstract']:
            summary = summarize_abstract(
                entry['abstract'],
                openai_api_key,
                model)
        else:
            summary = ""
        sender.send_summary(entry, summary)
        sleep(1)

    for ret in retrievers:
        ret.update_log()


if __name__ == '__main__':
    main()
