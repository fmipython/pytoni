# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

pytoni is a FastAPI backend serving an [agno](https://github.com/agno-agi/agno) AI agent
("course manager") for a Python course. A separate Discord bot is the only client; it
authenticates to the `/chat` endpoint with short-lived JWTs and conversations are
persisted to SQLite.

## Commands

Dependency management is via **uv** (Python 3.14).

```bash
uv sync                                   # install deps into .venv
uv run fastapi dev main.py                # run with auto-reload (dev)
uv run fastapi run main.py                # run production-style (host 0.0.0.0:8000)

# Migrations (run after changing src/pytoni/db_models.py)
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head

# Docker (runs migrations on startup, persists DB to the pytoni-data volume)
docker compose up --build
```

There is no test suite or linter configured yet.

## Architecture

The FastAPI app lives in `main.py` at the **repo root** (not inside the package); the
importable code is the `pytoni` package under `src/` (installed by `uv sync` via
hatchling). The single `/chat` route ties together four subsystems:

- **Auth** (`src/pytoni/auth.py`, `src/pytoni/config.py`) — `verify_token` is a FastAPI
  dependency that decodes an HS256 JWT (algorithm pinned, requires `exp`/`iss`/`aud`)
  using the shared `JWT_SECRET`. It returns `TokenClaims` (`discord_id`, `discord_name`).
  Rejected requests get `401` and never reach the agent or DB. Settings come from
  `pytoni.config.Settings` (pydantic-settings, reads `.env`).

- **Agent** (`src/pytoni/agents/course_manager.py`) — `create_agent()` builds a fresh
  agno `Agent` **per request**, backed by OpenRouter (needs `OPENROUTER_API_KEY` at
  runtime). Its system prompt is in `src/pytoni/prompts/course_manager.py` and it is
  given the tools in `src/pytoni/tools/`.

- **Persistence** (`src/pytoni/database.py`, `src/pytoni/db_models.py`) — synchronous
  SQLAlchemy. `database.py` exposes `engine`/`SessionLocal`/`Base`/`get_db`;
  `DATABASE_URL` is read from env, defaulting to `sqlite:///pytoni.db`. Each `/chat`
  call writes one `Message` row.

### Two distinct model layers — do not conflate

- `src/pytoni/models.py` — **Pydantic** request/response DTOs (`UserMessage`,
  `AssistantMessage`), each with an auto-generated UUID `id`.
- `src/pytoni/db_models.py` — **SQLAlchemy ORM** (`Message`). Its `discord_id` /
  `discord_name` columns are populated from the verified JWT claims, **not** from the
  request body, so they cannot be spoofed independently of the bot secret.

### Tools (external dependencies)

- `tools/fetch_readme.py` reads `COURSE_README.md` from the **current working
  directory** — so the server must run from the repo root.
- `tools/course_timeline.py::get_calendar` shells out to `uv run main.py get-calendar`
  in a **hardcoded sibling repo path** (`/Users/lyuboslav.karev/fmipython/course-db`).
  This path is machine-specific and will break elsewhere (including in Docker).

## Alembic

`alembic/env.py` is wired to the app: it imports `pytoni.database.Base` and
`pytoni.db_models` (so autogenerate sees the models) and sets `sqlalchemy.url` from
`DATABASE_URL`.

**SQLite caveat:** SQLite cannot `ADD COLUMN ... NOT NULL` without a default. When
adding a required column to a table that already has rows, hand-edit the generated
migration to add the column with a temporary `server_default` inside
`batch_alter_table`, then drop the default in a second `batch_alter_table` block (see
`alembic/versions/7a200c081912_add_discord_info_columns.py`).

## Required environment

Set in `.env` (see `.env.example`): `JWT_SECRET` (must be identical on the bot and the
backend), `OPENROUTER_API_KEY`, and optionally `DATABASE_URL`.
