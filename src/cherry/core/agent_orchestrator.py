import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import opentelemetry.trace as trace
from opentelemetry.metrics import Counter, Histogram, get_meter

# Configure logging
logger = logging.getLogger("cherry.agent")

# Configure OpenTelemetry
tracer = trace.get_tracer("cherry.agent.orchestrator")
meter = get_meter("cherry.agent.orchestrator")

# Metrics
agent_execution_time = Histogram("agent_execution_time", description="Time taken for agent execution")
agent_success_counter = Counter("agent_success_count", description="Number of successful agent executions")
agent_error_counter = Counter("agent_error_count", description="Number of failed agent executions")

class AgentInfo:
    """Information about a registered agent"""
    def __init__(self, handler: Callable, options: Dict[str, Any] = None):
        self.handler = handler
        self.options = options or {}
        self.status = "idle"
        self.last_run = None
        self.success_count = 0
        self.error_count = 0
        self.avg_execution_time = 0.0
        
        # Set default options if not provided
        if "timeout" not in self.options:
            self.options["timeout"] = 60  # Default 60 second timeout
        if "retries" not in self.options:
            self.options["retries"] = 0  # Default no retries


class AgentOrchestrator:
    """
    Core orchestration system for managing agents, executing tasks, and 
    handling inter-agent communication.
    
    This is the foundational class that manages all agent registration,
    execution, and coordination.
    """
    
    def __init__(self, max_concurrent: int = 4, cache_age: int = 1800):
        """
        Initialize the agent orchestrator.
        
        Args:
            max_concurrent: Maximum number of concurrent agent tasks
            cache_age: Cache expiration in seconds (default 30 minutes)
        """
        self.agents = {}  # Dict of agent_name -> AgentInfo
        self.cache = {}   # Dict of cache_key -> {"result": Any, "timestamp": int}
        self.active_tasks = set()  # Set of active task IDs
        self.pending_tasks = []    # List of pending tasks
        self.max_concurrent = max_concurrent
        self.cache_age = cache_age
        self.message_bus = {}      # Dict of agent_name -> List[Dict] for messages
        self.lock = asyncio.Lock() # Lock for thread safety
    
    def register_agent(self, name: str, handler: Callable, options: Dict[str, Any] = None) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            name: Unique identifier for the agent
            handler: Function that implements the agent's logic
            options: Configuration options for the agent
        """
        if not name or not isinstance(name, str):
            raise TypeError("Agent name must be a non-empty string")
        if not callable(handler):
            raise TypeError("Agent handler must be a callable function")
        
        if name in self.agents:
            logger.warning(f"Agent {name} is being overwritten")
        
        self.agents[name] = AgentInfo(handler, options)
        logger.info(f"Agent registered: {name}")
    
    async def execute_task(self, agent_name: str, params: Dict[str, Any] = None) -> Any:
        """
        Execute a task using the specified agent.
        
        Args:
            agent_name: Name of the agent to execute the task
            params: Parameters to pass to the agent
            
        Returns:
            Result from the agent execution
        """
        with tracer.start_as_current_span(f"execute_task_{agent_name}"):
            # Validate inputs
            if not agent_name:
                logger.error("Missing required parameter: agent_name")
                raise ValueError("Agent name is required")
            
            if agent_name not in self.agents:
                logger.error(f"Unknown agent: {agent_name}")
                raise ValueError(f"Agent not found: {agent_name}")
            
            # Create cache key
            params = params or {}
            try:
                cache_key = f"{agent_name}:{json.dumps(params, sort_keys=True)}"
            except (TypeError, ValueError) as e:
                logger.error(f"Failed to serialize params for cache key: {str(e)}")
                cache_key = None
            
            # Check cache
            if cache_key and cache_key in self.cache:
                cached = self.cache[cache_key]
                if time.time() - cached["timestamp"] < self.cache_age:
                    logger.debug(f"Cache hit for {agent_name}", extra={"params": params})
                    return cached["result"]
                # Cache expired
                del self.cache[cache_key]
            
            # Execute task directly or queue it if at concurrency limit
            async with self.lock:
                if len(self.active_tasks) >= self.max_concurrent:
                    # Queue the task
                    future = asyncio.Future()
                    self.pending_tasks.append({
                        "agent_name": agent_name,
                        "params": params,
                        "future": future
                    })
                    logger.debug(f"Task queued: {agent_name} (queue length: {len(self.pending_tasks)})")
                    return await future
                else:
                    # Execute directly
                    return await self._execute_task_directly(agent_name, params, cache_key)
    
    async def _execute_task_directly(
            self, agent_name: str, params: Dict[str, Any], 
            cache_key: Optional[str] = None) -> Any:
        """Internal method to execute a task directly."""
        agent = self.agents[agent_name]
        task_id = f"{agent_name}-{uuid.uuid4()}"
        
        # Track active task
        self.active_tasks.add(task_id)
        
        # Measure performance
        start_time = time.time()
        try:
            # Update agent status
            agent.status = "working"
            agent.last_run = datetime.now()
            
            # Execute with timeout
            agent_handler = agent.handler
            timeout = agent.options.get("timeout", 60)
            
            # Create task with timeout
            result = await asyncio.wait_for(
                asyncio.create_task(agent_handler(params)), 
                timeout=timeout
            )
            
            # Cache the result if we have a valid cache key
            if cache_key:
                self.cache[cache_key] = {
                    "result": result,
                    "timestamp": time.time()
                }
            
            # Update stats
            agent.success_count += 1
            agent_success_counter.add(1, {"agent": agent_name})
            
            return result
        except asyncio.TimeoutError:
            agent.error_count += 1
            agent_error_counter.add(1, {"agent": agent_name, "error": "timeout"})
            logger.error(f"Agent execution timeout: {agent_name}")
            raise TimeoutError(f"Task execution timeout: {agent_name}")
        except Exception as e:
            agent.error_count += 1
            agent_error_counter.add(1, {"agent": agent_name, "error": "exception"})
            logger.error(f"Agent execution error: {agent_name}", extra={"error": str(e)})
            raise
        finally:
            # Update execution time stats
            execution_time = time.time() - start_time
            logger.info(f"Agent {agent_name} execution time: {execution_time:.2f}s")
            # Remove the task from active tasks to prevent buildup
            self.active_tasks.remove(task_id)    
    async def _process_next_pending_task(self) -> None:
        """Process the next task in the pending queue."""
        async with self.lock:
            if self.pending_tasks and len(self.active_tasks) < self.max_concurrent:
                next_task = self.pending_tasks.pop(0)
                try:
                    # Execute the task
                    agent_name = next_task["agent_name"]
                    params = next_task["params"]
                    future = next_task["future"]
                    
                    # Create cache key
                    try:
                        cache_key = f"{agent_name}:{json.dumps(params, sort_keys=True)}"
                    except (TypeError, ValueError):
                        cache_key = None
                    
                    # Execute the task and set the result in the future
                    result = await self._execute_task_directly(agent_name, params, cache_key)
                    future.set_result(result)
                except Exception as e:
                    # Set exception in the future
                    next_task["future"].set_exception(e)
    
    async def send_message(self, from_agent: str, to_agent: str, message: Dict[str, Any]) -> None:
        """
        Send a message from one agent to another.
        
        Args:
            from_agent: Name of the sending agent
            to_agent: Name of the receiving agent
            message: Message content
        """
        if to_agent not in self.agents:
            raise ValueError(f"Target agent not found: {to_agent}")
            
        if to_agent not in self.message_bus:
            self.message_bus[to_agent] = []
            
        # Add timestamp and sender to message
        full_message = {
            "from": from_agent,
            "timestamp": time.time(),
            "message_id": str(uuid.uuid4()),
            "content": message
        }
        
        self.message_bus[to_agent].append(full_message)
        logger.debug(f"Message sent from {from_agent} to {to_agent}", extra={"message_id": full_message["message_id"]})
    
    async def get_messages(self, agent_name: str, clear: bool = True) -> List[Dict[str, Any]]:
        """
        Get messages for a specific agent.
        
        Args:
            agent_name: Name of the agent to get messages for
            clear: Whether to clear the messages after retrieval
            
        Returns:
            List of messages for the agent
        """
        if agent_name not in self.message_bus:
            return []
            
        messages = self.message_bus[agent_name]
        
        if clear:
            self.message_bus[agent_name] = []
            
        return messages
    
    def get_agent_stats(self) -> List[Dict[str, Any]]:
        """Get performance statistics for all registered agents."""
        try:
            return [
                {
                    "name": name,
                    "status": agent.status,
                    "success_count": agent.success_count,
                    "error_count": agent.error_count,
                    "avg_execution_time": agent.avg_execution_time,
                    "last_run": agent.last_run.isoformat() if agent.last_run else None
                }
                for name, agent in self.agents.items()
            ]
        except Exception as e:
            logger.error(f"Failed to get agent stats: {str(e)}")
            return []  # Return empty array rather than failing
    
    def clear_cache(self) -> int:
        """
        Clear the agent result cache.
        
        Returns:
            Number of cache entries cleared
        """
        try:
            size = len(self.cache)
            self.cache.clear()
            logger.info(f"Cache cleared: {size} entries removed")
            return size
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
            return 0
