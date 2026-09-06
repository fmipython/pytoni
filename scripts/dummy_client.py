"""Dummy Discord-bot stand-in for testing the /chat endpoint locally.

Mints a JWT the same way the real bot would (same claims verify_token expects)
and posts a chat message. Requires JWT_SECRET in .env / env to match the server.

Usage:
    uv run fastapi dev main.py &          # start the server first
    uv run scripts/dummy_client.py "What is the deadline for HW1?"
"""

import argparse
import sys
import time

import dotenv
import httpx
import jwt

dotenv.load_dotenv()

from pytoni.config import get_settings  # noqa: E402


def make_token(discord_id: str, discord_name: str) -> str:
    settings = get_settings()
    now = int(time.time())
    payload = {
        "discord_id": discord_id,
        "discord_name": discord_name,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": now + 60,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message", help="message to send to the agent")
    parser.add_argument("--url", default="http://127.0.0.1:8000/chat")
    parser.add_argument("--discord-id", default="123456789")
    parser.add_argument("--discord-name", default="dummy-user")
    args = parser.parse_args()

    token = make_token(args.discord_id, args.discord_name)
    response = httpx.post(
        args.url,
        json={"message": args.message},
        headers={"Authorization": f"Bearer {token}"},
        timeout=60,
    )
    response.raise_for_status()
    print(response.json()["message"])


if __name__ == "__main__":
    sys.exit(main())
