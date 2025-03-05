import logging
import os
import sys
from typing import Optional, Dict, Any, Union

from cherry.core.logging.handlers import ConsoleHandler, RotatingFileHandler
from cherry.core.logging.formatters import ColoredFormatter, JsonFormatter
from cherry.core.logging.config import LogConfig, load_config


class CherryLogger:
    """
    Advanced logger for the Cherry framework with support for different
    log levels, formatting options, and log rotation.
    """
    # Log levels mapping
    LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    def __init__(
        self,
        name: str,
        level: str = "info",
        format_str: Optional[str] = None,
        log_file: Optional[str] = None,
        console: bool = True,
        json_format: bool = False,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        config: Optional[Union[Dict[str, Any], str]] = None
    ):
        """
        Initialize the Cherry logger.

        Args:
            name: The name of the logger
            level: Log level (debug, info, warning, error, critical)
            format_str: Custom format string for log messages
            log_file: Path to the log file
            console: Whether to output logs to console
            json_format: Use JSON formatting for logs
            max_bytes: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
            config: Configuration dict or path to config file
        """
        self.name = name
        self.logger = logging.getLogger(name)
        
        # If config is provided, load it
        if config is not None:
            config_dict = load_config(config) if isinstance(config, str) else config
            cfg = LogConfig(**config_dict)
            self._configure_from_config(cfg)
            return

        # Set log level
        self.set_level(level)

        # Clear existing handlers
        self.logger.handlers = []

        # Set propagation
        self.logger.propagate = False

        # Default format if not provided
        if format_str is None:
            format_str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

        # Add console handler if requested
        if console:
            self._add_console_handler(format_str, json_format)

        # Add file handler if requested
        if log_file:
            self._add_file_handler(log_file, format_str, json_format, max_bytes, backup_count)

    def _configure_from_config(self, config: LogConfig):
        """Configure the logger from a LogConfig object."""
        self.set_level(config.level)
        self.logger.handlers = []
        self.logger.propagate = config.propagate

        if config.console_enabled:
            self._add_console_handler(config.format, config.json_format)
        
        if config.file_enabled and config.log_file:
            self._add_file_handler(
                config.log_file, 
                config.format, 
                config.json_format,
                config.max_bytes, 
                config.backup_count
            )

    def _add_console_handler(self, format_str: str, json_format: bool = False):
        """Add a console handler to the logger."""
        console_handler = ConsoleHandler()
        if json_format:
            formatter = JsonFormatter()
        else:
            formatter = ColoredFormatter(format_str)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _add_file_handler(
        self, 
        log_file: str, 
        format_str: str, 
        json_format: bool = False,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5
    ):
        """Add a file handler to the logger with rotation support."""
        # Ensure directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=max_bytes, 
            backupCount=backup_count
        )
        
        if json_format:
            formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(format_str)
            
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def set_level(self, level: str):
        """Set the log level."""
        level_value = self.LEVELS.get(level.lower(), logging.INFO)
        self.logger.setLevel(level_value)

    def add_handler(self, handler):
        """Add a custom handler to the logger."""
        self.logger.addHandler(handler)

    def debug(self, message, *args, **kwargs):
        """Log a debug message."""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        """Log an info message."""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        """Log a warning message."""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        """Log an error message."""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        """Log a critical message."""
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message, *args, exc_info=True, **kwargs):
        """Log an exception with traceback."""
        self.logger.exception(message, *args, exc_info=exc_info, **kwargs)


# Global logger registry
_loggers = {}

def get_logger(
    name: str = "cherry",
    level: str = "info",
    log_file: Optional[str] = None,
    **kwargs
) -> CherryLogger:
    """
    Get or create a logger with the given name.
    
    Args:
        name: Logger name
        level: Log level
        log_file: Log file path
        **kwargs: Additional logger configuration options
        
    Returns:
        A CherryLogger instance
    """
    global _loggers
    
    if name in _loggers:
        return _loggers[name]
        
    logger = CherryLogger(name, level, log_file=log_file, **kwargs)
    _loggers[name] = logger
    
    return logger
