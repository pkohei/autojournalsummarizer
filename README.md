# 最新論文をGPTで要約してDiscordに通知してくれるBot

n番煎じですが、論文の公開情報をGPTを使って要約してDiscordに通知してくれるBotを作りました。

こちらで簡単に解説しています。 [Qiita](https://qiita.com/para-yama/items/bc4de2b26416ea8b419b)

## Dockerを利用した使用方法

Dockerfileと同階層に `.env`ファイルを作成する

```sh
OPENAI_API_KEY={your-api-key}
DISCORD_URL={your-webhook-url}
```

ビルド＆ラン

```bash
docker compose build
docker compose run --rm journalgpt pipenv run python main.py
```

定期的に実行したければcronなどを使ってください。頻度は常識の範囲内にしましょう。
