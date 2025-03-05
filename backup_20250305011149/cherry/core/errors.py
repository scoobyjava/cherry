"""
Custom exceptions for the Cherry orchestration system.
"""
from typing import Optional, Any, Dict


class CherryError(Exception):
    """Base exception class for all Cherry-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class OrchestratorError(CherryError):
    """Base exception for orchestrator-related errors."""
    pass


class AgentError(CherryError):
    """Base exception for agent-related errors."""
    
    def __init__(self, message: str, agent_id: Optional[str] = None, 
                 agent_type: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        super().__init__(message, details)


class AgentTimeoutError(AgentError):
    """Exception raised when an agent operation times out."""
    
    def __init__(self, message: str, timeout_seconds: float, 
                 agent_id: Optional[str] = None, agent_type: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.timeout_seconds = timeout_seconds
        super().__init__(message, agent_id, agent_type, details)


class AgentExecutionError(AgentError):
    """Exception raised when an agent fails during execution."""
    
    def __init__(self, message: str, agent_id: Optional[str] = None, 
                 agent_type: Optional[str] = None, original_exception: Optional[Exception] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.original_exception = original_exception
        details = details or {}
        if original_exception:
            details['original_exception'] = str(original_exception)
            details['exception_type'] = type(original_exception).__name__
        super().__init__(message, agent_id, agent_type, details)


class MemoryError(CherryError):
    """Exception raised for memory-related errors."""
    pass


class ConfigurationError(CherryError):
    """Exception raised for configuration-related errors."""
    pass


class CherryException(Exception):
    """Base exception class for all Cherry AI exceptions."""
    pass

class OrchestratorException(CherryException):
    """Base exception for orchestrator-related errors."""
    pass

class AgentException(CherryException):
    """Base exception for agent-related errors."""
    def __init__(self, agent_id, message="Agent error occurred"):
        self.agent_id = agent_id
        self.message = f"Agent '{agent_id}': {message}"
        super().__init__(self.message)

class AgentExecutionError(AgentException):
    """Raised when an agent fails during execution of a task."""
    pass

class AgentCommunicationError(AgentException):
    """Raised when communication with an agent fails."""
    pass

class AgentTimeoutError(AgentException):
    """Raised when an agent operation times out."""
    pass

class AgentNotFoundError(OrchestratorException):
    """Raised when an agent is not found."""
    pass

class MemoryAccessError(CherryException):
    """Raised when there is an error accessing the memory store."""
    pass

class RecoveryFailedError(OrchestratorException):
    """Raised when a recovery attempt fails."""
    pass
