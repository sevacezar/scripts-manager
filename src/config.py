"""Application configuration settings."""

import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Scripts Manager"
    app_version: str = "0.1.0"
    environment: str = Field(default='development')
    log_level: str = Field(default='INFO')
    debug: bool = False

    # Scripts directory
    scripts_dir: Path = Path(__file__).parent.parent / "scripts"
    
    # Uploads directory for file storage
    uploads_dir: Path = Path(__file__).parent.parent / "uploads"
    
    # Security
    max_script_execution_time: int = 300  # seconds
    max_file_size: int = 100 * 1024 * 1024  # 100 MB
    allowed_script_extensions: set[str] = {".py"}
    
    # API
    api_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.scripts_dir.mkdir(parents=True, exist_ok=True)
settings.uploads_dir.mkdir(parents=True, exist_ok=True)

