# syntax=docker/dockerfile:1

# ---- Builder: resolve and install dependencies with uv ----
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies first (cached) using only the lock + manifest.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then install the project itself.
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ---- Runtime: slim image with just the venv + app ----
FROM python:3.14-slim-bookworm

WORKDIR /app

# Copy the application and its prebuilt virtualenv from the builder.
COPY --from=builder /app /app

# Put the venv on PATH so `fastapi`/`alembic`/`python` resolve to it.
ENV PATH="/app/.venv/bin:$PATH"

# Persist the SQLite database outside the image layer by default.
ENV DATABASE_URL="sqlite:////app/data/pytoni.db"

# Run as a non-root user; give it ownership of the data directory.
RUN mkdir -p /app/data \
    && useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app/data \
    && chmod +x /app/docker-entrypoint.sh
USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
