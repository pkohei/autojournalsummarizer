# AutoJournalSummarizer

arXiVの最新論文を要約し、Discordに通知してくれるシステムです。下記機能があります。

- GPTによりキーワードに基づく関心度に応じて更新された論文をフィルタリング
- 論文のPDF全文を読んだ上で要約
- Discordへの通知
- Google DriveにPDFをアップロード
- Zoteroに書誌情報を登録

旧バージョン(v1.0)については[Qiita](https://qiita.com/para-yama/items/bc4de2b26416ea8b419b)で簡単に解説しています。

## 開発環境構築

### 前提条件

- Docker & Docker Compose
- Visual Studio Code (推奨)
- Dev Containers拡張機能 (VS Code使用時)

### 開発環境セットアップ

1. 環境変数ファイルを作成:
```bash
# .envファイルを作成
OPENAI_API_KEY={your-api-key}
DISCORD_URL={your-webhook-url}
ZOTERO_API_KEY={your-api-key}
ZOTERO_LIBRARY_ID={your-library-id}
```

2. 設定ファイルを作成:
```bash
# settings/keywords.txt を作成
自然言語処理
画像解析
etc...
```

3. Google Drive認証ファイルを配置:
[こちら](https://yururi-do.com/backup-from-vps-to-gdrive-with-pydrive2/)を参考に、Googleサービスアカウントの`client_secret.json`を取得し、`auth/`ディレクトリに配置する。

最終的なファイル構成:
```
autojournalsummarizer/
├── .env
├── auth/
│   └── client_secret.json
└── settings/
    └── keywords.txt
```

### 開発方法

#### DevContainer使用 (推奨)
1. VS Codeでプロジェクトを開く
2. コマンドパレット (Ctrl+Shift+P) で "Dev Containers: Reopen in Container" を実行
3. 自動的にClaude Code CLI、Python、uvがセットアップされます

#### Docker Compose使用
```bash
# 開発環境起動
docker compose up dev

# コンテナに入る
docker compose exec dev bash

# 依存関係インストール
uv sync

# アプリケーション実行
python -m autojournalsummarizer.main
```

### 開発ツール

```bash
# コードフォーマット
uv run ruff format

# リンティング
uv run ruff check --fix

# 型チェック
uv run mypy src

# テスト実行
uv run pytest

# AI支援開発
claude
```

## 本番環境実行

```bash
# 本番環境でのワンショット実行
docker compose run --rm --build prod

# 継続実行 (バックグラウンド)
docker compose up -d prod
```

定期実行にはcronまたはコンテナオーケストレーションツールを使用してください。
