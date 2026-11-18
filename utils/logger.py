"""
Logger Utility Module.

Provides centralized Python logging configuration with formatted console output.
"""

import logging
import sys


def setup_logger(name: str = "asset_intelligence", log_level: str = "INFO") -> logging.Logger:
    """
    Configure and return a standard logger instance.

    Args:
        name (str): Name of the logger instance.
        log_level (str): String representation of log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if already setup
    if logger.handlers:
        return logger

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Console log handler formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
