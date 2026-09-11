"""
Logging module for cloud-automation-lab.

Provides consistent logging across all tasks and modules.
Never logs sensitive information such as passwords, tokens, or API keys.
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "automation", level: int = logging.INFO) -> logging.Logger:
    """Create and configure a logger instance.

    Args:
        name: Logger name (default: "automation")
        level: Logging level (default: logging.INFO)

    Returns:
        Configured Logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if logger already configured
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Console handler with clean formatting
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="[%(levelname)s] %(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Retrieve an existing logger or create a new one.

    Args:
        name: Logger name (optional)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(name)

    return logging.getLogger("automation")


# Sensitive field names that should never be logged
SENSITIVE_FIELDS = {
    "password",
    "token",
    "secret",
    "api_key",
    "api key",
    "api_key_id",
    "access_key",
    "secret_key",
    "auth",
    "authorization",
    "cookie",
    "session",
    "credential",
    "private_key",
    "pem",
    "passphrase",
    "jwt",
    "bearer",
}


def sanitize_message(message: str) -> str:
    """Remove or mask sensitive information from log messages.

    Args:
        message: Original log message

    Returns:
        Sanitized log message
    """
    lower_msg = message.lower()
    for field in SENSITIVE_FIELDS:
        if field in lower_msg:
            return f"[LOG REDACTED — message contained potential sensitive field '{field}']"
    return message


def safe_log(logger: logging.Logger, level: int, message: str) -> None:
    """Log a message after sanitizing it for sensitive content.

    Args:
        logger: Logger instance
        level: Logging level constant
        message: Message to log
    """
    sanitized = sanitize_message(message)
    logger.log(level, sanitized)