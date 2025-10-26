"""
Logging configuration using loguru

Centralizes logging setup for the application.
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_file_logging: bool = True,
    rotation: str = "10 MB",
    retention: str = "30 days",
) -> None:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (optional)
        enable_file_logging: Whether to enable file logging
        rotation: Log rotation size/time
        retention: How long to keep logs
    """
    # Remove default handler
    logger.remove()

    # Add console handler with nice formatting
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # Add file handler if enabled
    if enable_file_logging and log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip",
        )

        logger.info(f"File logging enabled: {log_file}")

    logger.info(f"Logging configured: level={log_level}")


def get_logger(name: str):
    """
    Get a logger instance for a module.

    Args:
        name: Module name (usually __name__)

    Returns:
        Logger instance
    """
    return logger.bind(name=name)
