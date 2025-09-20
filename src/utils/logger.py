"""Logging configuration for the MarketTwits Summarizer."""

import os
import sys
from loguru import logger
from .config import config


def setup_logger():
    """Set up the logger with appropriate configuration."""
    # Remove default handler
    logger.remove()
    
    # Add console handler with color
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # Add file handler for all logs
    log_file = os.path.join(config.LOGS_DIR, "market_twits.log")
    os.makedirs(config.LOGS_DIR, exist_ok=True)
    
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    # Add error file handler
    error_log_file = os.path.join(config.LOGS_DIR, "errors.log")
    logger.add(
        error_log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="1 day",
        retention="90 days",
        compression="zip"
    )
    
    return logger


# Initialize logger
setup_logger()
