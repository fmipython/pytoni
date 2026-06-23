# pytoni

AI agents for the Python Course.

A FastAPI backend that exposes a `/chat` endpoint backed by an [agno](https://github.com/agno-agi/agno)
agent. Requests are authenticated with short-lived JWTs minted by the Discord bot
(a separate service) and conversations are persisted to SQLite.

## Course manager agent

Responsible for answering questions around the timelines of the course — lectures,
homeworks, projects and grading.

## Requirements

- Python 3.14
- [uv](https://docs.astral.sh/uv/) for dependency management
- (Optional) Docker, for running in a container

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

Copy the example env file and fill in the values:

```bash
cp .env.example .env
```

| Variable             | Required | Description                                                                 |
| -------------------- | -------- | --------------------------------------------------------------------------- |
| `JWT_SECRET`         | yes      | Shared HMAC secret used to sign (bot) and verify (backend) chat JWTs.        |
| `OPENROUTER_API_KEY` | yes      | API key for OpenRouter, used by the course manager agent.                    |
| `DATABASE_URL`       | no       | SQLAlchemy URL. Defaults to `sqlite:///pytoni.db` (local file).             |

#### Generating the JWT secret

`JWT_SECRET` must be a long random value and **identical on the bot and the backend**.
Generate one with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Put the result in `.env` as `JWT_SECRET=...`. Use a 32+ byte value (the command above
produces enough entropy); short secrets are rejected by good practice and warned about
by PyJWT.

### 3. Apply database migrations

```bash
uv run alembic upgrade head
```

### 4. Run the server

```bash
# Development (auto-reload)
uv run fastapi dev main.py

# Production-style
uv run fastapi run main.py --host 0.0.0.0 --port 8000
```

The API is then available at http://localhost:8000 (interactive docs at `/docs`).

## Authentication

The `/chat` route requires a Bearer JWT signed with `JWT_SECRET` (HS256). The token
identifies the calling Discord user and proves the request comes from the bot. Required
claims:

| Claim          | Value                                |
| -------------- | ------------------------------------ |
| `iss`          | `pytoni-discord-bot`                  |
| `aud`          | `pytoni-backend`                      |
| `discord_id`   | the Discord user's id                 |
| `discord_name` | the Discord user's display name       |
| `exp`, `iat`   | short expiry (e.g. ~60s)              |

The bot (separate repo) mints tokens like this:

```python
import jwt, time

def make_token(discord_id: str, discord_name: str) -> str:
    now = int(time.time())
    return jwt.encode(
        {
            "iss": "pytoni-discord-bot",
            "aud": "pytoni-backend",
            "sub": discord_id,
            "discord_id": discord_id,
            "discord_name": discord_name,
            "iat": now,
            "exp": now + 60,
        },
        JWT_SECRET,  # same secret as the backend
        algorithm="HS256",
    )
```

Calling the endpoint:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"message": "When is the next homework due?"}'
```

Requests without a valid, unexpired token receive `401` and never reach the agent
or the database.

## Docker

The image is multi-stage (built with the `uv` base image) and runs migrations on
startup via `docker-entrypoint.sh` before launching the server as a non-root user.

### With docker compose (recommended)

`docker-compose.yml` mounts a named volume for the SQLite database and reads `.env`:

```bash
docker compose up --build
```

The database is persisted in the `pytoni-data` volume (mounted at `/app/data`); the
default `DATABASE_URL` in the image points there.

### With plain Docker

```bash
docker build -t pytoni:latest .

docker run --rm -p 8000:8000 \
  --env-file .env \
  -v pytoni-data:/app/data \
  pytoni:latest
```

## Database migrations

After changing an ORM model in `src/pytoni/db_models.py`, generate and apply a
migration:

```bash
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head
```

> Note: SQLite cannot add a `NOT NULL` column without a default. When adding required
> columns to a table that already has rows, edit the generated migration to add the
> column with a temporary `server_default` (inside `batch_alter_table`) and then drop
> the default.
