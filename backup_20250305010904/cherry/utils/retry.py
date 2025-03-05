import time
import logging
import functools
from typing import Callable, Type, Union, List, Optional

logger = logging.getLogger(__name__)

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception
):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier applied to delay between retries
        exceptions: Exception(s) that trigger a retry
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Failed after {max_attempts} attempts: {e}")
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt} failed with error: {e}. "
                        f"Retrying in {current_delay:.2f}s..."
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
                    attempt += 1
                    
        return wrapper
    return decorator
