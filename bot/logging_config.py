"""
Centralized logging configuration.

Logs go to both the console (INFO+) and a rotating log file (DEBUG+),
so every API request, response, and error is captured for the
deliverables required by the task (log files for MARKET and LIMIT orders).
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")


def setup_logging(log_file: str = LOG_FILE, level: int = logging.DEBUG) -> logging.Logger:
    """Configure and return the application logger.

    - File handler: DEBUG level, rotating (1MB x 5 backups), captures everything
      including raw API requests/responses.
    - Console handler: INFO level, human-readable summary only (keeps CLI output clean).
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger("trading_bot")
    logger.setLevel(level)
    logger.propagate = False

    # Avoid duplicate handlers if setup_logging() is called more than once
    if logger.handlers:
        return logger

    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_formatter = logging.Formatter(fmt="%(levelname)s: %(message)s")

    file_handler = RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
