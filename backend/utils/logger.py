"""
logger.py — Structured logger factory for the RAG Chatbot backend.

Usage
-----
    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Processing request", extra={"video_id": "abc123"})
"""

import logging
import sys
from backend.config import settings


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger configured with:
    - ISO-8601 timestamps
    - Log level from settings.LOG_LEVEL
    - Stream handler writing to stdout (Docker / cloud friendly)

    Calling get_logger() multiple times with the same name returns the
    same logger instance (Python's logging module guarantees this).

    Parameters
    ----------
    name : str
        Typically ``__name__`` of the calling module.

    Returns
    -------
    logging.Logger
    """
    logger = logging.getLogger(name)

    # Only add a handler if none exist yet (prevents duplicate log lines
    # when the module is imported multiple times in tests).
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    logger.propagate = False   # avoid double-logging when root logger is configured

    return logger
