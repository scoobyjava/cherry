from abc import ABC, abstractmethod
from typing import Dict, Any, List

class Agent(ABC):
    """Base class for all Cherry AI agents."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return the result."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities this agent has."""
        pass
