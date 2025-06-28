# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**IMPORTANT**: All content in this file should be written in English to maintain consistency and clarity.

## Project Overview

AutoJournalSummarizer is a Python application that automatically summarizes the latest papers from arXiv and sends notifications to Discord. The system includes:

- GPT-powered filtering based on keyword relevance
- Full PDF text reading and summarization
- Discord notifications
- Google Drive PDF uploads
- Zotero bibliography management

## Development Environment

This project uses DevContainer for consistent development environment across machines.

### Quick Start

1. Open the project in VS Code
2. Run "Dev Containers: Reopen in Container" from Command Palette
3. Install dependencies: `uv sync`
4. Start coding!

## Development Commands

### Package Management

```bash
# Install dependencies
uv sync

# Add new package
uv add package-name

# Add development package
uv add --dev package-name

# Update dependencies
uv lock --upgrade
```

When installing dependencies, use `uv add` instead of editing pyproject.toml directly. pyproject.toml will be automatically updated.


### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_main.py
```


### Code Quality

```bash
# Format code
uv run ruff format

# Run linting
uv run ruff check

# Auto-fix linting errors
uv run ruff check --fix
```


### Type Checking

```bash
# Run type checking
uv run mypy src
```


### Pre-commit Hooks

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run hooks on all files
uv run pre-commit run --all-files
```

## Project Architecture

- **Source code**: `src/{{ project_name.replace('-', '_') }}/` - Main application code
- **Tests**: `tests/` - Test files using pytest
- **Configuration**: `pyproject.toml` - Project configuration and dependencies
- **Dependencies**: `uv.lock` - Dependency lock file for reproducible builds
- **Docker**: `.devcontainer/` - Development container configuration
- **Production**: `Dockerfile.production` - Production-optimized Docker image

### Key Technologies

- **Python {{ python_version }}**: Programming language
- **uv**: Fast Python package manager
- **pytest**: Testing framework
- **ruff**: Code formatter and linter
- **mypy**: Static type checker
- **pre-commit**: Git hooks for code quality

## Development Guidelines

### Development workflow

**Follow this workflow for development unless otherwise specified by the user**

1. Create and present a development plan before starting work
2. Create a GitHub issue once the development plan is approved by the user
3. Before starting development, checkout the default branch, run `git pull` to get the latest commits from remote repository, and create a new branch from that commit
4. Start development on the branch created in step 3 according to the issue
5. Make commits and pushes with appropriate granularity during development
6. Create a PR after development is complete
7. Address review feedback and make necessary modifications if reviews are received
8. After PR is approved and merged, delete the branch, checkout the default branch, and run `git pull` to get the latest commits

### Code Style

- Use `ruff format` for code formatting
- Follow ruff linting rules (`ruff check`)
- Add type hints to all functions and methods
- Run `mypy` before committing changes
- Follow Python naming conventions (PEP 8)
- Write docstrings for public functions and classes

### Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)


## Gemini CLI Integration Guide

### Overview

When a user instructs **"proceed while consulting with Gemini"** (or similar instructions), Claude should proceed with the task in collaboration with **Gemini CLI**. Responses obtained from Gemini should be presented as-is, with additional explanations from Claude to combine insights from both agents.

### Trigger Examples

- "Proceed while consulting with Gemini"
- "Let's work on this while talking with Gemini"

### Command Execution

```
gemini --yolo -p "{instruction content}"
```

### Important Notes

Gemini tends to actively execute file editing tasks unless specifically instructed otherwise. If you don't want Gemini to perform irreversible operations, you must clearly add "please do not perform any operations" to the instruction content.

## Troubleshooting

### Common Issues

1. **Dependency conflicts**: Run `uv lock --upgrade` to resolve
2. **Import errors**: Ensure you're in the correct virtual environment

### Getting Help

- Review uv documentation: https://docs.astral.sh/uv/
