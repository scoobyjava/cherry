# agent.py
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from config import Config
from logger import logger
from agents.agent_factory import AgentFactory
from agents.base import Agent
from agents.researcher import ResearcherAgent
from agents.code_generator import CodeGeneratorAgent
from agents.creative import CreativeAgent

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
        try:
            # Validate input data
            if not isinstance(task_data, dict):
                raise ValueError("Input data must be a dictionary")

            # Process data
            pass

        except asyncio.CancelledError:
            logger.warning("Task was cancelled")
            raise

        except ValueError as ve:
            logger.error(f"ValueError: {ve}")
            # Handle specific value error

        except KeyError as ke:
            logger.error(f"KeyError: Missing key {ke}")
            # Handle missing key error

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            # Handle any other unexpected errors

        finally:
            # Cleanup actions if necessary
            pass

    def can_handle(self, task_description: str) -> bool:
        """
        Determine if this agent can handle the given task based on its capabilities.
        """
        return any(capability.lower() in task_description.lower() for capability in self.capabilities)

    def __str__(self):
        return f"{self.name}: {self.description}"


class ResearchAgent(Agent):
    """Agent specialized in information gathering and research."""

    def __init__(self):
        super().__init__(
            name="Research Agent",
            description="Specialized in gathering information and conducting research"
        )
        self.capabilities = ["research", "find information", "search", "investigate", "analyze data"]

    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        query = task_data.get("description", "")
        logger.info(f"🔍 {self.name} processing query: {query}")
        try:
            # Placeholder for actual search implementation
            await asyncio.sleep(0.1)  # Simulate async operation
            result = {
                "agent": self.name,
                "result": f"Research completed for query: {query}",
                "source": "Simulated database"
            }
            return result
        except asyncio.CancelledError:
            logger.warning("Task was cancelled")
            raise
        except ValueError as ve:
            logger.error(f"ValueError: {ve}")
            return {"agent": self.name, "error": str(ve)}
        except KeyError as ke:
            logger.error(f"KeyError: Missing key {ke}")
            return {"agent": self.name, "error": str(ke)}
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return {"agent": self.name, "error": str(e)}
        finally:
            # Cleanup actions if necessary
            pass

class AgentFactory:
    """Factory class for creating and managing agents."""
    
    _agent_types = {
        "researcher": ResearcherAgent,
        "code_generator": CodeGeneratorAgent,
        "creative": CreativeAgent,
    }
    
    @classmethod
    def register_agent_type(cls, agent_type: str, agent_class: Type[Agent]) -> None:
        """Register a new agent type."""
        cls._agent_types[agent_type] = agent_class
    
    @classmethod
    def create_agent(cls, agent_type: str, agent_id: str, config: Optional[Dict[str, Any]] = None) -> Agent:
        """Create an agent of the specified type."""
        if agent_type not in cls._agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        return cls._agent_types[agent_type](agent_id, config)

class AgentManager:
    """Manager class for handling multiple agents."""
    
    def __init__(self):
        self.agents = {}
    
    async def initialize_agent(self, agent_type: str, agent_id: str, config: Optional[Dict[str, Any]] = None) -> Agent:
        """Initialize and register a new agent."""
        if agent_id in self.agents:
            raise ValueError(f"Agent with ID {agent_id} already exists")
        
        agent = AgentFactory.create_agent(agent_type, agent_id, config)
        await agent.initialize()
        self.agents[agent_id] = agent
        return agent
    
    async def process_request(self, agent_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request with the specified agent."""
        if agent_id not in self.agents:
            return {"status": "error", "message": f"Agent with ID {agent_id} not found"}
        
        return await self.agents[agent_id].handle_request(request)
    
    async def cleanup(self) -> None:
        """Clean up all agents."""
        cleanup_tasks = [agent.cleanup() for agent in self.agents.values()]
        await asyncio.gather(*cleanup_tasks)
        self.agents = {}
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by its ID."""
        return self.agents.get(agent_id)

async def example_usage():
    """Example of how to use the AgentManager."""
    manager = AgentManager()
    
    # Initialize agents
    await manager.initialize_agent("researcher", "research-1", {"sources": ["web", "academic"]})
    await manager.initialize_agent("code_generator", "codegen-1", {"languages": ["python", "javascript", "rust"]})
    await manager.initialize_agent("creative", "creative-1", {"styles": ["narrative", "poetic", "technical"]})
    
    # Process requests
    research_result = await manager.process_request("research-1", {"query": "latest AI advancements"})
    code_result = await manager.process_request("codegen-1", {"specification": "Create a sorting algorithm", "language": "python"})
    creative_result = await manager.process_request("creative-1", {"prompt": "A story about a wise AI", "style": "narrative"})
    
    # Clean up
    await manager.cleanup()

if __name__ == "__main__":
    # Example of running the agents
    asyncio.run(example_usage())
