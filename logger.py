import logging
import os
from config import config

def setup_logger(name=None):
    """Configure and return a logger instance"""
    name = name or config.app_name
    
    # Create logs directory if it doesn't exist
    log_file_path = config.logging.file_path
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    
    # Set up logger with configuration from config system
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.logging.level.upper()))
    
    # File handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(logging.Formatter(config.logging.format))
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(config.logging.format))
    logger.addHandler(console_handler)
    
    return logger

# Example usage
logger = setup_logger(__name__)
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
