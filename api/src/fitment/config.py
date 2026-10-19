from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# api/src/fitment/config.py -> repo root, where .env lives. In containers the
# file is absent and Compose supplies the same names as environment variables.
REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://fitment:fitment@localhost:5432/fitment"
    redis_url: str = "redis://localhost:6379/0"
    admin_token: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
