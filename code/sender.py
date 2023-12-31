import json
import time

import requests


class DiscordSender:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_summary(self, entry, summary):
        message = f'# {entry["title"]}\n' \
            '## 概要\n' \
            f'著者: {", ".join(entry["authors"])}\n' \
            f'日付: {time.strftime("%Y-%m-%d %H:%M%z", entry["updated"])}\n' \
            f'URL: {entry["link"]}\n\n' \
            f'{summary}\n'

        print('------------------------------')
        print(message)

        headers = {'Content-Type': 'application/json'}
        data = {'content': message}
        res = requests.post(
            self.webhook_url, data=json.dumps(data), headers=headers)

        print(res.status_code)
