import json
import logging
import os
from datetime import datetime, timezone

from agno.run.agent import RunOutput

from pytoni.auth import TokenClaims

LOG_FILE = os.getenv("AGENT_LOG_FILE", "agent_usage.log")

usage_logger = logging.getLogger("pytoni.usage")
usage_logger.setLevel(logging.INFO)
usage_logger.propagate = False
if not usage_logger.handlers:
    handler = logging.FileHandler(LOG_FILE)
    handler.setFormatter(logging.Formatter("%(message)s"))
    usage_logger.addHandler(handler)


def log_chat_usage(claims: TokenClaims, user_message: str, response: RunOutput) -> None:
    """Append one JSON line per /chat call: who asked, what the agent did, tokens used."""
    metrics = response.metrics
    usage_logger.info(
        json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "discord_id": claims.discord_id,
                "discord_name": claims.discord_name,
                "user_message": user_message,
                "model": response.model,
                "tools_used": [
                    {"tool": t.tool_name, "args": t.tool_args} for t in (response.tools or [])
                ],
                "input_tokens": metrics.input_tokens if metrics else 0,
                "output_tokens": metrics.output_tokens if metrics else 0,
                "cache_read_tokens": metrics.cache_read_tokens if metrics else 0,
                "cache_write_tokens": metrics.cache_write_tokens if metrics else 0,
                "reasoning_tokens": metrics.reasoning_tokens if metrics else 0,
                "total_tokens": metrics.total_tokens if metrics else 0,
                "cost": metrics.cost if metrics else None,
            },
            default=str,
        )
    )
