# Multi-stage build for optimal caching and size
# Stage 1: Base with uv
FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim as uv-base

# Install Python and system dependencies first
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    sudo \
    ca-certificates \
    gpg \
    locales \
    libsndfile1 \
    && localedef -f UTF-8 -i ja_JP ja_JP.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

# Set locale
ENV LANG=ja_JP.UTF-8 LANGUAGE=ja_JP:ja LC_ALL=ja_JP.UTF-8 TZ=JST-9

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for Claude Code CLI
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Create a non-root user
RUN useradd -m -s /bin/bash vscode && \
    echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Configure uv environment variables for optimal Docker usage
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/home/vscode/.cache/uv
ENV UV_PYTHON_PREFERENCE=only-system

# Create cache directory and Claude Code directory with proper permissions
RUN mkdir -p /home/vscode/.cache/uv /home/vscode/.claude && \
    chown -R vscode:vscode /home/vscode/.cache /home/vscode/.claude

# Set working directory
WORKDIR /workspace

# Create virtual environment directory
RUN mkdir -p /workspace/.venv && chown vscode:vscode /workspace/.venv

# Switch to vscode user
USER vscode

# Set environment variables for development
ENV PYTHONUNBUFFERED=1
ENV PATH="/workspace/.venv/bin:$PATH"

# Stage 2: Development stage with dependencies
FROM uv-base as development

# Copy project configuration files for dependency resolution
COPY --chown=vscode:vscode pyproject.toml ./

# Temporarily switch to root to create lock file, then switch back
USER root

# Install dependencies for faster rebuilds (including dev dependencies)
RUN uv sync --no-install-project && \
    chown vscode:vscode uv.lock 2>/dev/null || true

# Copy the rest of the project
COPY --chown=vscode:vscode . ./

# Install project in development mode with all dev dependencies
RUN if [ -f "README.md" ]; then \
    uv sync; \
    else \
    echo "README.md not found, skipping project installation"; \
    touch README.md; \
    uv sync; \
    rm README.md; \
    fi && \
    chown -R vscode:vscode .venv uv.lock 2>/dev/null || true

# Switch back to vscode user
USER vscode

# Ensure vscode user has access to uv cache
RUN mkdir -p /home/vscode/.cache/uv 2>/dev/null || true

# Default command
CMD ["/bin/bash"]
