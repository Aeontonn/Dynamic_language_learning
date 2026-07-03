from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Application settings, loaded from environment variables or a .env file."""

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/language_learning"
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-5"

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")


settings = Settings()
