"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

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

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
