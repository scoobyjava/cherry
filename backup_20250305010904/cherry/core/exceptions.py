"""
Custom exceptions for the Cherry orchestrator.
"""

class CherryException(Exception):
    """Base exception for all Cherry-related errors."""
    pass

class AgentException(CherryException):
    """Base exception for agent-related errors."""
    def __init__(self, agent_id, message="Agent operation failed"):
        self.agent_id = agent_id
        self.message = f"Agent {agent_id}: {message}"
        super().__init__(self.message)

class AgentInitializationError(AgentException):
    """Raised when an agent fails to initialize."""
    def __init__(self, agent_id, details=None):
        message = f"Failed to initialize agent"
        if details:
            message += f" - {details}"
        super().__init__(agent_id, message)

class AgentExecutionError(AgentException):
    """Raised when an agent fails during execution."""
    def __init__(self, agent_id, task=None, details=None):
        message = f"Failed during execution"
        if task:
            message += f" of task '{task}'"
        if details:
            message += f" - {details}"
        super().__init__(agent_id, message)

class OrchestratorException(CherryException):
    """Base exception for orchestrator-related errors."""
    pass

class WorkflowException(OrchestratorException):
    """Raised when a workflow fails to execute properly."""
    pass

class ResourceUnavailableException(OrchestratorException):
    """Raised when a required resource is unavailable."""
    pass
