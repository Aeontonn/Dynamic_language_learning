from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables or a .env file."""

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/language_learning"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
