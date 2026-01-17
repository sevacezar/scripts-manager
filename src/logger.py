"""Logger setup"""

import logging
import sys

import structlog

from src.config import settings


def configure_logging(log_level: str = settings.log_level) -> None:
    """Configure the logging system with structlog and standard logging.

    This function sets up both standard Python logging and structlog with
    appropriate processors and formatters based on the environment.

    Args:
        log_level (str, optional): The logging level to use. Defaults to LOG_LEVEL
            environment variable or "INFO".

    Note:
        In development environment, logs are rendered to console with colors.
        In other environments, logs are rendered as JSON.
    """
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level),
    )
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    if settings.environment == "development":
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer(ensure_ascii=False))
    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance for the specified name.

    Args:
        name (str): The name of the logger, typically __name__ of the module.

    Returns:
        structlog.stdlib.BoundLogger: A configured logger instance.
    """
    return structlog.get_logger(name)


configure_logging()
