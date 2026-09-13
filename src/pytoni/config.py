from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Shared secret used to sign/verify the Discord bot's JWTs. Required.
    jwt_secret: str

    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "pytoni-discord-bot"
    jwt_audience: str = "pytoni-backend"
    # Small allowance for clock skew between the bot and the backend (seconds).
    jwt_leeway_seconds: int = 10

    # Base URL of the course-db service (exposes GET /calendar).
    course_db_url: str = "http://localhost:8001"


@lru_cache
def get_settings() -> Settings:
    return Settings()
