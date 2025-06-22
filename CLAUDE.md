# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
- **pre-commit**: Automated code quality checks
- **GitHub Actions**: Automated CI/CD workflows

## Key Commands

### Development
```bash
# Start development environment
docker compose up dev

# Or use DevContainer in VS Code (recommended)
# Command Palette -> "Dev Containers: Reopen in Container"

# Install dependencies
uv sync

# Run the application (production mode)
python -m autojournalsummarizer.main

# Run in test mode (processes papers without sending notifications)
python -m autojournalsummarizer.main --test

# Run with custom parameters
python -m autojournalsummarizer.main --num_papers 10 --model gpt-4o-mini

# Run single test
uv run pytest tests/test_main.py::test_placeholder -v
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

# Run tests with coverage
uv run pytest --cov=autojournalsummarizer --cov-report=html

# Pre-commit hooks (automatically run on commit)
uv run pre-commit run --all-files

# Install pre-commit hooks (one-time setup)
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
```

### Production
```bash
# Build and run production container
docker compose up --build prod

# One-shot execution
docker compose run --rm --build prod

# Background execution
docker compose up -d prod
```

### CI/CD
This project uses GitHub Actions for automated testing and code quality checks:

- **CI Workflow** (`.github/workflows/ci.yml`): Runs on every push and PR
  - Linting with ruff (check and format)
  - Type checking with mypy
  - Testing with pytest across Python 3.10, 3.11, and 3.12
  - Code coverage reporting

- **Pre-commit Workflow** (`.github/workflows/pre-commit.yml`): Validates code quality
- **Test Workflow** (`.github/workflows/test.yml`): Focused testing with coverage

All workflows use uv for fast dependency management and include caching for optimal performance.

## Architecture

### Core Workflow
The application follows a pipeline architecture:

1. **Paper Retrieval**: Fetches recent papers from arXiv in the specified category (cs.LG)
2. **Filtering**: Uses OpenAI structured outputs to filter papers based on user-defined keywords
3. **Processing**: For each interesting paper:
   - Downloads PDF
   - Extracts text using pypdf
   - Generates structured summary using GPT
   - Sends Discord notification
   - Uploads to Google Drive
   - Registers in Zotero bibliography
   - Updates last processed timestamp

### Data Models (Pydantic)
- `Paper`: Represents a filtered paper with index, title, and selection reason
- `Papers`: Collection of filtered papers
- `PaperSummary`: Structured summary with Japanese title, summary sections, and keywords
- `Keyword`: Individual keyword with explanation

### File-based State Management
- `settings/last_date.txt`: Tracks last processed paper timestamp
- `settings/keywords.txt`: User-defined research interests (one per line)
- `prompts/filter_prompt.txt`: Template for paper filtering (uses {keywords} placeholder)
- `prompts/summarize_prompt.txt`: Template for paper summarization

### External Integrations
- **OpenAI**: Uses structured outputs (`beta.chat.completions.parse`) for consistent JSON responses
- **arXiv**: Searches by category and date range, downloads PDFs
- **Discord**: Webhook-based notifications with rich markdown formatting
- **Google Drive**: Service account authentication, uploads to "papers" folder
- **Zotero**: Creates preprint items in "daily" collection with PDF attachments

## Configuration

Required configuration files:

1. `.env` file with API keys:
   ```
   OPENAI_API_KEY=your-api-key
   DISCORD_WEBHOOK_URL=your-webhook-url
   ZOTERO_API_KEY=your-api-key
   ZOTERO_LIBRARY_ID=your-library-id
   ```

2. `settings/keywords.txt`: Research keywords (one per line in Japanese)
3. `auth/client_secret.json`: Google service account credentials
4. `settings/auth_settings.yaml`: Google Drive authentication settings

## Development Workflow

This project follows a feature branch workflow for all development:

### Starting New Work
```bash
# Always start from main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/descriptive-name
# or
git checkout -b fix/bug-description
```

### Development Process
1. **Code Changes**: Make your modifications in the feature branch
2. **Quality Checks**:
   ```bash
   # Format and lint
   uv run ruff format
   uv run ruff check --fix

   # Type checking
   uv run mypy src

   # Run tests
   uv run pytest
   ```
3. **Commit**: Use appropriate commit message conventions
   - Pre-commit hooks will automatically run
   - Ensure all hooks pass before pushing

### Creating Pull Requests
```bash
# Push feature branch
git push -u origin feature/your-branch-name

# Create PR with GitHub CLI
gh pr create --title "Descriptive title" --body "
## Summary
Brief description of changes

## Test plan
- [ ] Manual testing steps
- [ ] Automated tests added/updated
"
```

### After PR Merge
```bash
# Return to main and clean up
git checkout main
git pull origin main
git branch -d feature/your-branch-name
```

### Branch Naming Conventions
- **Features**: `feature/add-new-functionality`
- **Bug fixes**: `fix/resolve-specific-issue`
- **Documentation**: `docs/update-readme`
- **Refactoring**: `refactor/improve-code-structure`

## Development Principles

- **Branch Management**:
  - 作業開始時はmainブランチをpullし、その最新コミット上でブランチを切り、その新しいブランチ上で作業すること。

## Dependencies

Main dependencies:
- `openai`: GPT API integration with structured outputs
- `arxiv`: arXiv paper access and PDF downloads
- `pyzotero`: Zotero bibliography management
- `pydrive2`: Google Drive uploads with service account auth
- `pypdf`: PDF text extraction
- `pydantic`: Data validation and structured outputs

Development dependencies:
- `ruff`: Linting and formatting
- `mypy`: Type checking
- `pytest`: Testing framework
- `pre-commit`: Automated code quality hooks
- `jupyterlab`: Interactive development
