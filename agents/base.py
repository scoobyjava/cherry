# agent.py
import abc
import asyncio
from typing import Dict, Any, Optional, List
from config import Config
from logger import logger
from cherry.core.messaging import MessagingSystem
import time
import logging
import traceback
from typing import Dict, Any, Optional, Tuple
from cherry.core.errors import AgentException, AgentExecutionError, AgentTimeoutError

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for all agents in the Cherry system."""
    
    def __init__(self):
        self.name = self.__class__.__name__
        logger.info(f"Initialized {self.name}")
        
    def process(self, request: Dict[str, Any], memories: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Process a request with optional memories for context.
        
        Args:
            request: The request to process
            memories: List of relevant memories to provide context
            
        Returns:
            Response dictionary
        """
        raise NotImplementedError("Each agent must implement its process method")
    
    def _format_memories_as_context(self, memories: List[Dict[str, Any]]) -> str:
        """Format memories into a string that can be used as context."""
        if not memories:
            return "No relevant past information available."
            
        context = "Relevant past information:\n\n"
        for i, memory in enumerate(memories):
            context += f"[Memory {i+1}]: {memory['content']}\n\n"
            
        return context

class Agent(BaseAgent, abc.ABC):
    """Base Agent class that all specialized agents should inherit from."""
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.agent_id = agent_id
        self.config = config or {}
        self.is_busy = False
        self._capabilities = []
        self.health_status = "healthy"
        self.last_error = None
        self.error_count = 0
        self.last_health_check = time.time()
    
    @abc.abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request asynchronously and return the result."""
        pass
    
    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize any resources needed by the agent."""
        pass
    
    async def cleanup(self) -> None:
        """Clean up any resources used by the agent."""
        pass
    
    @property
    def agent_type(self) -> str:
        """Return the type of the agent."""
        return self.__class__.__name__
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming request, managing the busy state."""
        if self.is_busy:
            return {"status": "error", "message": f"Agent {self.agent_id} is busy"}
        
        try:
            self.is_busy = True
            response = await self.process_request(request)
            return response
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            self.is_busy = False

    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities this agent has.
        
        Returns:
            List of capability strings
        """
        return self._capabilities
        
    def add_capability(self, capability: str):
        """
        Add a capability to this agent.
        
        Args:
            capability: The capability to add
        """
        if capability not in self._capabilities:
            self._capabilities.append(capability)

    def execute_with_error_handling(self, func_name, *args, **kwargs) -> Tuple[Any, Optional[Exception]]:
        """
        Execute a function with error handling.
        
        Args:
            func_name: The name of the function to execute
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Tuple containing (result, exception) where exception is None if no error occurred
        """
        try:
            if not hasattr(self, func_name):
                raise AttributeError(f"Function '{func_name}' not found in agent")
            
            start_time = time.time()
            func = getattr(self, func_name)
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if hasattr(self, 'update_metrics'):
                self.update_metrics(func_name, execution_time)
                
            return result, None
        except Exception as e:
            self.error_count += 1
            self.last_error = {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': time.time(),
                'function': func_name,
                'args': args,
                'kwargs': kwargs
            }
            self.health_status = "degraded" if self.error_count < 5 else "unhealthy"
            
            logger.error(f"Agent '{self.agent_id}' error in {func_name}: {e}")
            
            return None, AgentExecutionError(self.agent_id, f"Error in {func_name}: {str(e)}")
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check health status of the agent.
        
        Returns:
            Dict with health information
        """
        self.last_health_check = time.time()
        
        # Perform basic checks
        health_data = {
            "agent_id": self.agent_id,
            "status": self.health_status,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "last_health_check": self.last_health_check,
        }
        
        # Reset health status if no errors for a while
        if self.health_status != "healthy" and self.error_count == 0:
            self.health_status = "healthy"
            
        return health_data
        
    def reset_error_state(self):
        """Reset the error state of the agent."""
        self.error_count = 0
        self.last_error = None
        self.health_status = "healthy"
        logger.info(f"Agent '{self.agent_id}' error state reset")


class ResearchAgent(Agent):
    """Agent specialized in information gathering and research."""

    def __init__(self):
        super().__init__(
            agent_id="Research Agent",
            config={"description": "Specialized in gathering information and conducting research"}
        )
        self.capabilities = ["research", "find information", "search", "investigate", "analyze data"]

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        query = request.get("description", "")
        logger.info(f"🔍 {self.agent_id} processing query: {query}")
        try:
            # Placeholder for actual search implementation
            await asyncio.sleep(0.1)  # Simulate async operation
            result = {
                "agent": self.agent_id,
                "result": f"Research completed for query: {query}",
                "source": "Simulated database"
            }
            return result
        except asyncio.CancelledError:
            logger.warning(f"{self.agent_id} task was cancelled")
            raise
        except Exception as e:
            logger.error(f"{self.agent_id} encountered an error: {e}")
            return {"agent": self.agent_id, "error": str(e)}

    async def initialize(self) -> None:
        pass


class CreativeAgent(Agent):
    """Agent specialized in creative content generation."""

    def __init__(self):
        super().__init__(
            agent_id="Creative Agent",
            config={"description": "Specialized in generating creative content and ideas"}
        )
        self.capabilities = ["write", "create", "generate", "design", "creative", "story", "content"]

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        prompt = request.get("description", "")
        logger.info(f"🎨 {self.agent_id} generating creative content for: {prompt}")
        try:
            await asyncio.sleep(0.1)  # Simulate async operation
            result = {
                "agent": self.agent_id,
                "result": f"Creative content based on: {prompt}"
            }
            return result
        except asyncio.CancelledError:
            logger.warning(f"{self.agent_id} task was cancelled")
            raise
        except Exception as e:
            logger.error(f"{self.agent_id} encountered an error: {e}")
            return {"agent": self.agent_id, "error": str(e)}

    async def initialize(self) -> None:
        pass


class CodeAgent(Agent):
    """Agent specialized in code generation and software development tasks."""

    def __init__(self):
        super().__init__(
            agent_id="Code Agent",
            config={"description": "Specialized in generating code and solving programming problems"}
        )
        self.capabilities = ["code", "program", "develop", "script", "function", "algorithm", "debug"]

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        requirement = request.get("description", "")
        logger.info(f"💻 {self.agent_id} generating code for: {requirement}")
        try:
            await asyncio.sleep(0.1)  # Simulate async operation
            result = {
                "agent": self.agent_id,
                "result": f"Generated Python code for: {requirement}",
                "language": "python"
            }
            return result
        except asyncio.CancelledError:
            logger.warning(f"{self.agent_id} task was cancelled")
            raise
        except Exception as e:
            logger.error(f"{self.agent_id} encountered an error: {e}")
            return {"agent": self.agent_id, "error": str(e)}

    async def initialize(self) -> None:
        pass


class AnalyticsAgent(Agent):
    """Agent specialized in data analysis and visualization."""

    def __init__(self):
        super().__init__(
            agent_id="Analytics Agent",
            config={"description": "Specialized in analyzing data and creating visualizations"}
        )
        self.capabilities = ["analyze", "visualize", "chart", "graph", "data", "statistics", "trend"]

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        analysis_request = request.get("description", "")
        logger.info(f"📊 {self.agent_id} analyzing data for: {analysis_request}")
        try:
            await asyncio.sleep(0.1)  # Simulate async operation
            result = {
                "agent": self.agent_id,
                "result": f"Analysis report for: {analysis_request}",
                "visualization_type": "bar chart"
            }
            return result
        except asyncio.CancelledError:
            logger.warning(f"{self.agent_id} task was cancelled")
            raise
        except Exception as e:
            logger.error(f"{self.agent_id} encountered an error: {e}")
            return {"agent": self.agent_id, "error": str(e)}

    async def initialize(self) -> None:
        pass


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

        logger.info(f"✅ Agents loaded: {', '.join([agent.agent_id for agent in agents])}")
        return agents

    @staticmethod
    def get_agent_by_name(name: str) -> Optional[Agent]:
        """Get a specific agent by name."""
        agents = {agent.agent_id.lower(): agent for agent in AgentFactory.get_all_agents()}
        agent = agents.get(name.lower())
        if not agent:
            logger.warning(f"⚠️ Agent '{name}' not found.")
        return agent
