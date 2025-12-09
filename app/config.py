"""Application configuration."""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "Agent Execution Framework"
    app_version: str = "0.1.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # Use SQLite in-memory database for development without PostgreSQL
    database_url: str = "sqlite+aiosqlite:///:memory:"
    database_echo: bool = False

    max_loop_iterations: int = 100


settings = Settings()
