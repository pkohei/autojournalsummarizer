# Development environment using official uv image
FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    locales \
    libsndfile1 \
    && localedef -f UTF-8 -i ja_JP ja_JP.UTF-8 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set locale
ENV LANG=ja_JP.UTF-8 LANGUAGE=ja_JP:ja LC_ALL=ja_JP.UTF-8 TZ=JST-9

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -m -s /bin/bash appuser

# Set up workspace
WORKDIR /app
RUN chown appuser:appuser /app

USER appuser

# Configure uv for development
ENV UV_CACHE_DIR=/home/appuser/.cache/uv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy dependency files
COPY --chown=appuser:appuser pyproject.toml ./

# Install dependencies
RUN uv venv && uv sync

# Default command for development
CMD ["tail", "-f", "/dev/null"]