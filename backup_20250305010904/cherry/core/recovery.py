"""
Recovery strategies and utilities for handling errors in the orchestrator.
"""
import time
import logging
import functools
import random
from typing import Optional, Callable, TypeVar, Any, List, Dict, Type, Union

from cherry.core.errors import (
    CherryError, AgentError, AgentTimeoutError, AgentExecutionError
)

# Type variables for generic function signatures
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

logger = logging.getLogger(__name__)


class RetryStrategy:
    """Base class for retry strategies."""
    
    def get_next_delay(self, attempt: int) -> float:
        """Return the delay in seconds before the next retry."""
        raise NotImplementedError("Subclasses must implement get_next_delay")


class ConstantRetry(RetryStrategy):
    """Retry with a constant delay."""
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
    
    def get_next_delay(self, attempt: int) -> float:
        return self.delay


class ExponentialBackoff(RetryStrategy):
    """Retry with exponential backoff."""
    
    def __init__(self, initial_delay: float = 1.0, max_delay: float = 60.0, 
                 factor: float = 2.0, jitter: bool = True):
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.factor = factor
        self.jitter = jitter
    
    def get_next_delay(self, attempt: int) -> float:
        delay = min(self.initial_delay * (self.factor ** attempt), self.max_delay)
        if self.jitter:
            delay = delay * (0.5 + random.random())
        return delay


def retry(max_attempts: int = 3, 
          retry_strategy: RetryStrategy = None,
          retryable_exceptions: List[Type[Exception]] = None,
          on_retry: Callable[[Exception, int], None] = None) -> Callable[[F], F]:
    """
    Decorator that retries a function if it raises specified exceptions.
    
    Args:
        max_attempts: Maximum number of attempts including the first one
        retry_strategy: Strategy to determine delay between retries
        retryable_exceptions: List of exceptions that should trigger retry
        on_retry: Callback function to execute before retry
        
    Returns:
        Decorated function
    """
    retry_strategy = retry_strategy or ExponentialBackoff()
    retryable_exceptions = retryable_exceptions or [AgentError, ConnectionError]
    
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except tuple(retryable_exceptions) as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
                        raise
                    
                    delay = retry_strategy.get_next_delay(attempt)
                    if on_retry:
                        on_retry(e, attempt)
                    
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} for {func.__name__} "
                        f"failed: {str(e)}. Retrying in {delay:.2f}s"
                    )
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            return None
        
        return wrapper  # type: ignore
    
    return decorator


class ErrorRecoveryHandler:
    """
    Handles error recovery based on exception type and context.
    """
    
    def __init__(self, fallback_agents: Optional[Dict[str, List[str]]] = None):
        """
        Initialize error recovery handler.
        
        Args:
            fallback_agents: Mapping from agent types to a list of fallback agent types,
                            in order of preference
        """
        self.fallback_agents = fallback_agents or {}
    
    def handle_agent_error(self, error: AgentError, orchestrator: Any) -> Any:
        """
        Handle agent errors by trying fallback agents or partial results.
        
        Args:
            error: The agent error that occurred
            orchestrator: The orchestrator instance
            
        Returns:
            Result from successful fallback or partial result
            
        Raises:
            AgentError: If no recovery was possible
        """
        if isinstance(error, AgentTimeoutError):
            logger.warning(f"Agent {error.agent_id} timed out after {error.timeout_seconds}s")
            return self._try_fallback_agents(error, orchestrator)
        
        if isinstance(error, AgentExecutionError):
            logger.warning(f"Agent {error.agent_id} execution failed: {error.message}")
            return self._try_fallback_agents(error, orchestrator)
        
        # For unknown agent errors, just log and re-raise
        logger.error(f"Unhandled agent error: {error}")
        raise error
    
    def _try_fallback_agents(self, error: AgentError, orchestrator: Any) -> Any:
        """Try to use fallback agents if available."""
        if not error.agent_type or error.agent_type not in self.fallback_agents:
            logger.error(f"No fallback agents available for {error.agent_type}")
            raise error
        
        for fallback_type in self.fallback_agents[error.agent_type]:
            try:
                logger.info(f"Trying fallback agent of type {fallback_type}")
                # This is a placeholder for actual fallback logic that would be implemented
                # in the orchestrator. The actual implementation depends on the orchestrator API.
                fallback_result = orchestrator.execute_with_agent_type(fallback_type)
                return fallback_result
            except Exception as e:
                logger.warning(f"Fallback to {fallback_type} failed: {str(e)}")
        
        # If we get here, all fallbacks failed
        raise error
