# AutoJournalSummarizer

arXiVの最新論文を要約し、Discordに通知してくれるシステムです。下記機能があります。

- GPTによりキーワードに基づく関心度に応じて更新された論文をフィルタリング
- 論文のPDF全文を読んだ上で要約
- Discordへの通知
- Google DriveにPDFをアップロード
- Zoteroに書誌情報を登録

旧バージョン(v1.0)については[Qiita](https://qiita.com/para-yama/items/bc4de2b26416ea8b419b)で簡単に解説しています。

## 環境構築

`docker-compose.yml`と同階層に `.env`ファイルを作成する。

```sh
OPENAI_API_KEY={your-api-key}
DISCORD_URL={your-webhook-url}
ZOTERO_API_KEY={your-api-key}
ZOTERO_LIBRARY_ID={your-library-id}
```

`settings/`以下に`keywords.txt`を作成する。中身は関心のあるキーワードを箇条書きしたもの。

```text
自然言語処理
画像解析
etc...
```

[こちら](https://yururi-do.com/backup-from-vps-to-gdrive-with-pydrive2/)と[こちら](https://yururi-do.com/backup-to-gdrive-with-pydrive2-and-gas/#st-toc-h-2)を参考に、Googleサービスアカウントの`client_secret.json`を取得し、`auth`以下に配置する(OAuth認証の場合、個人＆無料利用ではリフレッシュトークンの有効期限が1週間になってしまうため、サービスアカウント認証とすること)。

最終的に下記のような配置になればよい。

```text
autojournalsummarizer/
    L auth/
        L client_secret.json
    L settings/
        L keywords.txt
    L .env
```

## 実行

```bash
docker compose run --rm --build prod
```

定期的に実行したければcronなどを使ってください。頻度は常識の範囲内にしましょう。
