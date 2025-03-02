# agent.py
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from config import Config
from logger import logger

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
        except Exception as e:
            logger.error(f"{self.name} encountered an error: {e}")
            return {"agent": self.name, "error": str(e)}


class CreativeAgent(Agent):
    """Agent specialized in creative content generation."""

    def __init__(self):
        super().__init__(
            name="Creative Agent",
            description="Specialized in generating creative content and ideas"
        )
        self.capabilities = ["write", "create", "generate", "design", "creative", "story", "content"]

    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = task_data.get("description", "")
        logger.info(f"🎨 {self.name} generating creative content for: {prompt}")
        try:
            await asyncio.sleep(0.1)  # Simulate async operation
            result = {
                "agent": self.name,
                "result": f"Creative content based on: {prompt}"
            }
            return result
        except Exception as e:
            logger.error(f"{self.name} encountered an error: {e}")
            return {"agent": self.name, "error": str(e)}


class CodeAgent(Agent):
    """Agent specialized in code generation and software development tasks."""

    def __init__(self):
        super().__init__(
            name="Code Agent",
            description="Specialized in generating code and solving programming problems"
        )
        self.capabilities = ["code", "program", "develop", "script", "function", "algorithm", "debug"]

    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        requirement = task_data.get("description", "")
        logger.info(f"💻 {self.name} generating code for: {requirement}")
        try:
            await asyncio.sleep(0.1)  # Simulate async operation
            result = {
                "agent": self.name,
                "result": f"Generated Python code for: {requirement}",
                "language": "python"
            }
            return result
        except Exception as e:
            logger.error(f"{self.name} encountered an error: {e}")
            return {"agent": self.name, "error": str(e)}


class AnalyticsAgent(Agent):
    """Agent specialized in data analysis and visualization."""

    def __init__(self):
        super().__init__(
            name="Analytics Agent",
            description="Specialized in analyzing data and creating visualizations"
        )
        self.capabilities = ["analyze", "visualize", "chart", "graph", "data", "statistics", "trend"]

    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        analysis_request = task_data.get("description", "")
        logger.info(f"📊 {self.name} analyzing data for: {analysis_request}")
        try:
            await asyncio.sleep(0.1)  # Simulate async operation
            result = {
                "agent": self.name,
                "result": f"Analysis report for: {analysis_request}",
                "visualization_type": "bar chart"
            }
            return result
        except Exception as e:
            logger.error(f"{self.name} encountered an error: {e}")
            return {"agent": self.name, "error": str(e)}


# Factory pattern for creating agents
class AgentFactory:
    """Factory class for creating and retrieving agents."""

    @staticmethod
    def get_all_agents() -> List[Agent]:
        """Return all available agents based on configuration."""
        agents = []

        if getattr(Config, "ENABLE_RESEARCH_AGENT", True):
            agents.append(ResearchAgent())

        if getattr(Config, "ENABLE_CREATIVE_AGENT", True):
            agents.append(CreativeAgent())

        if getattr(Config, "ENABLE_CODE_AGENT", True):
            agents.append(CodeAgent())

        if getattr(Config, "ENABLE_ANALYTICS_AGENT", True):
            agents.append(AnalyticsAgent())

        logger.info(f"✅ Agents loaded: {', '.join([agent.name for agent in agents])}")
        return agents

    @staticmethod
    def get_agent_by_name(name: str) -> Optional[Agent]:
        """Get a specific agent by name."""
        agents = {agent.name.lower(): agent for agent in AgentFactory.get_all_agents()}
        agent = agents.get(name.lower())
        if not agent:
            logger.warning(f"⚠️ Agent '{name}' not found.")
        return agent
