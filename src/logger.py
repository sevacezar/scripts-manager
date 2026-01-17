"""Logging configuration."""

import logging
import sys
from pathlib import Path

from src.config import settings


def setup_logger(name: str = "scripts_manager") -> logging.Logger:
    """Configure and return logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.propagate = False
    
    return logger


# Global logger instance
logger = setup_logger()

