import logging
import sys
from logging.handlers import RotatingFileHandler as BaseRotatingFileHandler


class ConsoleHandler(logging.StreamHandler):
    """
    A handler that writes log records to the console with optional coloring.
    """
    
    def __init__(self, stream=None):
        """
        Initialize the handler.
        
        Args:
            stream: The stream to use for output (default: sys.stderr)
        """
        if stream is None:
            stream = sys.stderr
        super().__init__(stream)


class RotatingFileHandler(BaseRotatingFileHandler):
    """
    Enhanced rotating file handler with additional features.
    """
    
    def __init__(
        self,
        filename,
        mode='a',
        maxBytes=0,
        backupCount=0,
        encoding=None,
        delay=False,
        errors=None
    ):
        """
        Initialize the handler.
        
        Args:
            filename: Log file name
            mode: File open mode
            maxBytes: Maximum file size before rotation
            backupCount: Number of backup files to keep
            encoding: File encoding
            delay: Delay opening file until first emit
            errors: Error handling scheme
        """
        super().__init__(
            filename,
            mode=mode,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay,
            errors=errors
        )


class MemoryHandler(logging.Handler):
    """
    A handler that keeps log records in memory, useful for testing or temporary storage.
    """
    
    def __init__(self, capacity=1000, flushLevel=logging.ERROR):
        """
        Initialize the handler.
        
        Args:
            capacity: Maximum number of records to store
            flushLevel: Level at which to flush the buffer
        """
        super().__init__()
        self.capacity = capacity
        self.flushLevel = flushLevel
        self.buffer = []
    
    def emit(self, record):
        """Emit a log record."""
        self.buffer.append(self.format(record))
        if len(self.buffer) > self.capacity:
            self.buffer.pop(0)
        if record.levelno >= self.flushLevel:
            self.flush()
    
    def flush(self):
        """Flush the buffer."""
        self.buffer = []
    
    def get_records(self):
        """Get all records in the buffer."""
        return self.buffer
