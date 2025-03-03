# logger.py
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from config import Config

logger = logging.getLogger(Config.APP_NAME)

def setup_logger():
    if logger.hasHandlers():
        logger.handlers.clear()

    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    console_formatter = logging.Formatter(
        fmt="📝 %(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    if Config.LOG_FILE:
        try:
            log_dir = os.path.dirname(Config.LOG_FILE)
            if log_dir:  # FIXED: safely handle empty directories
                os.makedirs(log_dir, exist_ok=True)

            file_handler = RotatingFileHandler(
                filename=Config.LOG_FILE,
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        except Exception as e:
            logger.error(f"🚨 Failed to initialize file logging: {e}")

    logger.propagate = False
    logger.info(f"✅ Logger initialized successfully with level '{Config.LOG_LEVEL}'")

    return logger

setup_logger()
