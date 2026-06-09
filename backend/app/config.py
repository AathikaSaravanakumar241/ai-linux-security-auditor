"""
Application configuration management via Pydantic Settings.

Loads all configuration from environment variables (or a .env file).
Uses @lru_cache to ensure a single Settings instance across the application.

Architecture Note:
    This is the single source of truth for all configurable values.
    Every service module imports `get_settings()` instead of reading
    os.environ directly, which makes testing and overriding trivial.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Central configuration loaded from environment variables.

    Attributes:
        DATABASE_URL: PostgreSQL connection string.
        GEMINI_API_KEY: Google Gemini API key for security analysis.
        GEMINI_MODEL: Gemini model identifier (default: gemini-2.0-flash).
        SSH_TIMEOUT: Seconds to wait for SSH connection establishment.
        SSH_COMMAND_TIMEOUT: Seconds to wait for a single command to finish.
        LOG_LEVEL: Python logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        CORS_ORIGINS: Comma-separated allowed origins for CORS.
    """

    # --- Database ---
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/linux_audit"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # --- Gemini AI ---
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # --- SSH Defaults ---
    SSH_TIMEOUT: int = 30
    SSH_COMMAND_TIMEOUT: int = 60

    # --- Application ---
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "*"  # Restrict in production

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance. Call once per process lifetime."""
    return Settings()
