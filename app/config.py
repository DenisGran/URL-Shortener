"""Settings read from environment variables (Heroku config vars) or a local .env file."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    base_url: str = "http://localhost:8000"

    @field_validator("database_url")
    @classmethod
    def _use_postgresql_scheme(cls, value: str) -> str:
        # Heroku sets DATABASE_URL as postgres://…; libpq accepts it, but SQLAlchemy-based
        # tools (Alembic's URL handling) reject it. Normalize once, here.
        if value.startswith("postgres://"):
            return "postgresql://" + value.removeprefix("postgres://")
        return value

    @field_validator("base_url")
    @classmethod
    def _strip_trailing_slash(cls, value: str) -> str:
        # short_url is built as f"{base_url}/{code}"; avoid a double slash.
        return value.rstrip("/")
