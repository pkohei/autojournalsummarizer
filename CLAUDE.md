# AutoJournalSummarizer - Claude Code Configuration

## Project Overview

AutoJournalSummarizer is a Python application that automatically summarizes the latest papers from arXiv and sends notifications to Discord. The system includes:

- GPT-powered filtering based on keyword relevance
- Full PDF text reading and summarization
- Discord notifications
- Google Drive PDF uploads
- Zotero bibliography management

## Development Environment

This project uses a modern Python development setup with:

- **uv**: Fast Python package manager
- **DevContainer**: VS Code containerized development
- **Claude Code**: AI-assisted development
- **ruff**: Code linting and formatting
- **mypy**: Type checking
- **pytest**: Testing framework

## Key Commands

### Development
```bash
# Start development environment
docker compose up dev

# Or use DevContainer in VS Code
# Command Palette -> "Dev Containers: Reopen in Container"

# Install dependencies
uv sync

# Run the application
python -m autojournalsummarizer.main
```

### Code Quality
```bash
# Format code
uv run ruff format

# Run linting
uv run ruff check --fix

# Type checking
uv run mypy src

# Run tests
uv run pytest
```

### Production
```bash
# Build and run production container
docker compose up --build prod
```

## Project Structure

```
autojournalsummarizer/
├── .devcontainer/          # DevContainer configuration
├── src/
│   └── autojournalsummarizer/  # Main source code
│       ├── __init__.py
│       └── main.py         # Application entry point
├── tests/                  # Test files
├── prompts/               # AI prompt templates
├── auth/                  # Authentication files
├── settings/              # Configuration files
├── pyproject.toml         # Dependencies and tool configuration
├── Dockerfile.production  # Production container
└── docker-compose.yml     # Development and production services
```

## Configuration

The application requires:

1. `.env` file with API keys:
   ```
   OPENAI_API_KEY=your-api-key
   DISCORD_URL=your-webhook-url
   ZOTERO_API_KEY=your-api-key
   ZOTERO_LIBRARY_ID=your-library-id
   ```

2. `settings/keywords.txt` with research keywords
3. `auth/client_secret.json` for Google Drive integration

## Dependencies

Main dependencies include:
- `openai`: GPT API integration
- `arxiv`: arXiv paper access
- `pyzotero`: Zotero integration
- `pydrive2`: Google Drive uploads
- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `pypdf`: PDF processing

Development dependencies:
- `ruff`: Linting and formatting
- `mypy`: Type checking
- `pytest`: Testing
- `jupyterlab`: Interactive development