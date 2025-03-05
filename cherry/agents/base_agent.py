# base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from cherry.utils.logger import logger

class Agent(ABC):
    """
    Base abstract class for all specialized agents in Cherry AI.
    Each agent has specific capabilities and responsibilities.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.capabilities = []
        logger.info(f"✨ Agent initialized: {self.name}")

    @abstractmethod
    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the task according to this agent's specialization.
        Must be implemented by all agent subclasses.
        """
        pass

    def can_handle(self, task_description: str) -> bool:
        """
        Determine if this agent can handle the given task based on its capabilities.
        """
        return any(capability.lower() in task_description.lower() for capability in self.capabilities)

    def __str__(self):
        return f"{self.name}: {self.description}"
