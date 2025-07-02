"""Central logging configuration for the Aperture backend.

This sets up:
1. A console handler for local development.
2. A WebSocketLogHandler so the front-end log viewer can receive streamed logs.

Call ``configure_logging()`` once at application startup *before* any
library initialises its own logger.
"""
from logging.config import dictConfig


def configure_logging() -> None:  # noqa: D401
    """Configure root logger with structured settings."""
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
                "websocket": {
                    "class": "backend.api.logger.WebSocketLogHandler",
                    "formatter": "default",
                },
            },
            "root": {
                "handlers": ["console", "websocket"],
                "level": "INFO",
            },
        }
    )
