"""Application configuration settings."""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Scripts Manager"
    app_version: str = "0.1.0"
    debug: bool = False

    # Scripts directory
    scripts_dir: Path = Path(__file__).parent.parent / "scripts"
    
    # Security
    max_script_execution_time: int = 300  # seconds
    max_file_size: int = 100 * 1024 * 1024  # 100 MB
    allowed_script_extensions: set[str] = {".py"}
    
    # API
    api_prefix: str = "/api/v1"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure scripts directory exists
settings.scripts_dir.mkdir(parents=True, exist_ok=True)

