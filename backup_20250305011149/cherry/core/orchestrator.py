import asyncio
import json
import time
import networkx as nx
from threading import Lock
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import threading
import logging

import openai
from config import Config
from logger import logger
from memory_chroma import ChromaMemory
from .tasks import TASKS
from .task_handlers import handle_task1, handle_task2
from .llm_interface import LLMInterface
from .llm_adapter_1 import LLMAdapter1
from .llm_adapter_2 import LLMAdapter2
from .task_queue import TaskQueue
from .agent_selector import AgentSelector

@dataclass
class TaskDependency:
    prerequisite_ids: List[int] = field(default_factory=list)
    blocking_conditions: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class TaskMetrics:
    attempts: int = 0
    success_rate: float = 0.0
    avg_processing_time: float = 0.0
    last_execution_time: float = 0.0
    total_processing_time: float = 0.0

class TaskOrchestrationError(Exception):
    pass

class AdvancedOrchestrator:
    def __init__(self, config_path: str = 'config.json'):
        self.task_queue = []
        self.completed_tasks = []
        self.task_dependency_graph = nx.DiGraph()
        self.task_metrics: Dict[int, TaskMetrics] = {}
        self.lock = Lock()
        self.running = False
        self.agent_performance: Dict[str, Dict[str, Any]] = {}

        self.load_configuration(config_path)
        self._init_memory_system()
        self.loop = asyncio.new_event_loop()
        self.lock = threading.Lock()
        self.tasks = []
        self.task_dependencies = {}
        logging.basicConfig(level=logging.DEBUG)

    def load_configuration(self, config_path: str):
        """Load configuration settings from a JSON file."""
        try:
            with open(config_path, 'r') as config_file:
                self.advanced_config = json.load(config_file)
        except FileNotFoundError:
            self.advanced_config = {
                "max_concurrent_tasks": 5,
                "task_timeout": 3600
            }

    def _init_memory_system(self):
        """Initialize the memory system using ChromaMemory."""
        try:
            self.primary_memory = ChromaMemory(collection_name="cherry_primary_memory")
            logger.info("Memory initialized successfully.")
        except Exception as e:
            logger.error(f"Memory initialization failed: {e}")

    def add_task(self, description: str, priority: int = 1, context: Optional[Dict[str, Any]] = None) -> int:
        """Add a new task to the queue and return its unique ID."""
        with self.lock:
            task_id = len(self.task_queue) + len(self.completed_tasks) + 1
            task = {
                "id": task_id,
                "description": description,
                "priority": priority,
                "context": context or {},
                "status": "pending",
                "created_at": time.time()
            }
            self.task_queue.append(task)
            self.task_dependency_graph.add_node(task_id)
            self.task_metrics[task_id] = TaskMetrics()
            logger.info(f"Task {task_id} added: {description}")
            logging.debug(f"Adding task {task_id} with dependencies {[]}")
            self.tasks.append(task_id)
            self.task_dependencies[task_id] = []
            self._check_for_cycles()
            return task_id

    def _check_for_cycles(self):
        visited = set()
        stack = set()

        def visit(task):
            if task in stack:
                logging.error(f"Cycle detected: {task} is in the stack {stack}")
                raise Exception("Task dependency cycle detected")
            if task not in visited:
                logging.debug(f"Visiting task {task}")
                stack.add(task)
                for dep in self.task_dependencies.get(task, []):
                    visit(dep)
                stack.remove(task)
                visited.add(task)

        for task in self.tasks:
            visit(task)

    def get_task_status(self, task_id: int) -> Dict[str, Any]:
        """Retrieve the status and details of a specific task by its ID."""
        with self.lock:
            for task in self.task_queue + self.completed_tasks:
                if task["id"] == task_id:
                    return task
            return {"error": f"Task {task_id} not found"}

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Return a list of all tasks, both queued and completed."""
        with self.lock:
            return self.task_queue + self.completed_tasks

    def clear_completed_tasks(self):
        """Clear the list of completed tasks."""
        with self.lock:
            self.completed_tasks.clear()
            logger.info("Completed tasks cleared")

    async def _process_task_with_llm(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task using a language model (placeholder implementation)."""
        description = task.get("description", "")
        logger.info(f"Processing task {task['id']} with LLM: {description}")
        try:
            # Placeholder: Replace with actual LLM API call in the future
            await asyncio.sleep(0.1)  # Simulate async processing
            output = f"Processed: {description}"
            task["status"] = "completed"
            task["result"] = output
            with self.lock:
                if task in self.task_queue:
                    self.task_queue.remove(task)
                    self.completed_tasks.append(task)
            return {"output": output}
        except asyncio.CancelledError:
            logger.info(f"Task {task['id']} was cancelled")
            raise
        except Exception as e:
            logger.error(f"LLM processing failed for task {task['id']}: {e}")
            task["status"] = "failed"
            return {"error": str(e)}

    async def _worker(self):
        """Background worker loop to process tasks from the queue."""
        while self.running:
            with self.lock:
                if self.task_queue:
                    task = self.task_queue.pop(0)  # Process tasks in FIFO order
                else:
                    task = None
            if task:
                await self._process_task_with_llm(task)
            await asyncio.sleep(1)  # Prevent busy-waiting when queue is empty

    def run(self):
        """Start the orchestrator and initiate the worker loop."""
        self.running = True
        logger.info("AdvancedOrchestrator running...")
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self._worker())
        self.loop.run_forever()

    def stop(self):
        """Stop the orchestrator and terminate the worker loop."""
        self.running = False
        self.loop.stop()
        logger.info("AdvancedOrchestrator stopped.")

    def execute_tasks(self):
        while self.tasks:
            with self.lock:
                for task in list(self.tasks):
                    if all(dep in self.completed_tasks for dep in self.task_dependencies[task]):
                        logging.debug(f"Executing task {task}")
                        self._execute_task(task)
                        self.tasks.remove(task)

    def _execute_task(self, task):
        # Simulate task execution
        logging.debug(f"Task {task} started")
        # ...existing task execution code...
        logging.debug(f"Task {task} completed")
        self.completed_tasks.append(task)

import importlib
import logging
from typing import Dict, Any, Optional, List, Callable

from .exceptions import (
    AgentException, AgentInitializationError, AgentExecutionError,
    OrchestratorException, WorkflowException, ResourceUnavailableException
)
from .recovery import RecoveryManager, RetryStrategy, FallbackAgentStrategy

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Orchestrates agent execution with robust error handling and recovery.
    """
    
    def __init__(self, default_agent_type: str = "default"):
        """
        Initialize the Orchestrator.
        
        Args:
            default_agent_type: The default agent to use when no specific agent is matched
        """
        self.agent_registry = {}
        self.capabilities = {}
        self.default_agent_type = default_agent_type
        self.logger = logging.getLogger(__name__)
        self.recovery_manager = RecoveryManager()
        self._setup_recovery_strategies()
        
    def _setup_recovery_strategies(self):
        """Set up default recovery strategies."""
        # Default retry strategy for most agent exceptions
        self.recovery_manager.register_strategy(
            AgentException, 
            RetryStrategy(max_retries=3, delay=2.0)
        )
        
        # The default strategy for any unhandled exception
        self.recovery_manager.set_default_strategy(
            RetryStrategy(max_retries=1, delay=1.0)
        )
    
    def register_agent(self, agent_type: str, agent_instance, capabilities: Optional[List[str]] = None):
        """
        Register an agent with the orchestrator.
        
        Args:
            agent_type: The type/name of the agent
            agent_instance: The agent instance
            capabilities: List of capabilities this agent has
        """
        self.agent_registry[agent_type] = agent_instance
        if capabilities:
            self.capabilities[agent_type] = capabilities
        self.logger.info(f"Registered agent: {agent_type}")
    
    def load_agent(self, agent_module: str, agent_class: str, agent_type: str = None, **kwargs):
        """
        Dynamically load and register an agent.
        
        Args:
            agent_module: The module path to the agent
            agent_class: The agent class name
            agent_type: The type name to register (defaults to agent_class)
            **kwargs: Arguments to pass to the agent constructor
        
        Returns:
            The agent instance
        """
        if agent_type is None:
            agent_type = agent_class
            
        try:
            module = importlib.import_module(agent_module)
            agent_cls = getattr(module, agent_class)
            agent_instance = agent_cls(**kwargs)
            
            # Extract capabilities if the agent has a get_capabilities method
            capabilities = None
            if hasattr(agent_instance, 'get_capabilities'):
                capabilities = agent_instance.get_capabilities()
                
            self.register_agent(agent_type, agent_instance, capabilities)
            return agent_instance
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to load agent {agent_class} from {agent_module}: {e}")
            return None
            
    def analyze_task(self, task: str) -> str:
        """
        Analyze the incoming task to determine which agent is best suited.
        
        Args:
            task: The task to analyze
            
        Returns:
            The type of agent best suited for this task
        """
        task_lower = task.lower()
        
        # Check each agent's capabilities against the task
        agent_scores = {}
        
        for agent_type, capability_list in self.capabilities.items():
            score = 0
            for capability in capability_list:
                if capability.lower() in task_lower:
                    score += 1
            agent_scores[agent_type] = score
        
        # Find the agent with the highest score
        if agent_scores:
            best_agent = max(agent_scores.items(), key=lambda x: x[1])
            if best_agent[1] > 0:  # If at least one capability matched
                return best_agent[0]
        
        # Fall back to keyword matching
        if "research" in task_lower or "information" in task_lower or "find" in task_lower:
            return "researcher" if "researcher" in self.agent_registry else self.default_agent_type
        elif "code" in task_lower or "programming" in task_lower or "develop" in task_lower:
            return "developer" if "developer" in self.agent_registry else self.default_agent_type
        elif "summarize" in task_lower or "write" in task_lower:
            return "writer" if "writer" in self.agent_registry else self.default_agent_type
        else:
            return self.default_agent_type
            
    def route_task(self, task: str, **kwargs) -> Any:
        """
        Route the task to the appropriate agent.
        
        Args:
            task: The task to route
            **kwargs: Additional arguments to pass to the agent
            
        Returns:
            The result from the agent processing the task
        
        Raises:
            ValueError: If no suitable agent is available
        """
        agent_type = self.analyze_task(task)
        self.logger.info(f"Routing task to agent: {agent_type}")
        
        if agent_type in self.agent_registry:
            agent = self.agent_registry[agent_type]
            return agent.process_task(task, **kwargs)
        else:
            error_msg = f"No agent available for task type: {agent_type}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
    
    def list_agents(self) -> List[str]:
        """
        List all registered agents.
        
        Returns:
            Names of registered agents
        """
        return list(self.agent_registry.keys())
        
    def get_agent(self, agent_type: str):
        """
        Get a specific agent by type.
        
        Args:
            agent_type: The type of agent to retrieve
            
        Returns:
            The agent instance or None if not found
        """
        return self.agent_registry.get(agent_type)
    
    def create_fallback_agent(self, failed_agent_id: str, context: Dict[str, Any]):
        """
        Create a fallback agent when primary agent fails.
        
        Args:
            failed_agent_id: ID of the failed agent
            context: Context with information about the failure
            
        Returns:
            A fallback agent instance or None if creation fails
        """
        try:
            # This would be implemented based on your agent factory pattern
            # For example:
            agent_class = context.get('agent_class')
            if agent_class:
                fallback_config = {
                    'is_fallback': True,
                    'original_agent_id': failed_agent_id,
                    # Simplified configuration that might help the agent succeed
                    'timeout': context.get('timeout', 30) * 2,  # Double timeout
                }
                
                fallback_agent = agent_class(f"{failed_agent_id}_fallback", **fallback_config)
                self.register_agent(f"{failed_agent_id}_fallback", fallback_agent)
                return fallback_agent
        except Exception as e:
            logger.error(f"Failed to create fallback agent for {failed_agent_id}: {str(e)}")
        
        return None
    
    def register_fallback_strategy(self, error_type: type) -> None:
        """
        Register a fallback agent strategy for a specific error type.
        
        Args:
            error_type: The error type to handle with fallback agents
        """
        self.recovery_manager.register_strategy(
            error_type,
            FallbackAgentStrategy(self.create_fallback_agent)
        )
    
    def register_workflow(self, workflow_id: str, workflow_steps: List[Dict[str, Any]]) -> None:
        """
        Register a workflow with the orchestrator.
        
        Args:
            workflow_id: Unique identifier for the workflow
            workflow_steps: List of steps defining the workflow
            
        Raises:
            OrchestratorException: If workflow registration fails
        """
        try:
            if workflow_id in self.workflows:
                logger.warning(f"Workflow {workflow_id} is already registered, replacing")
            
            self.workflows[workflow_id] = workflow_steps
            logger.info(f"Workflow {workflow_id} registered successfully with {len(workflow_steps)} steps")
        except Exception as e:
            error_msg = f"Failed to register workflow {workflow_id}: {str(e)}"
            logger.error(error_msg)
            raise OrchestratorException(error_msg)
    
    def execute_agent_task(self, agent_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with an agent and handle potential failures.
        
        Args:
            agent_id: ID of the agent to use
            task: Task definition to execute
            
        Returns:
            Dict with task results or error information
            
        Raises:
            AgentExecutionError: If execution fails and cannot be recovered
        """
        if agent_id not in self.agent_registry:
            raise AgentInitializationError(agent_id, "Agent not registered")
        
        agent = self.agent_registry[agent_id]
        
        try:
            logger.info(f"Executing task with agent {agent_id}: {task.get('type', 'unknown')}")
            result = agent.execute_task(task)
            logger.info(f"Agent {agent_id} completed task successfully")
            return result
        except Exception as e:
            logger.error(f"Agent {agent_id} failed to execute task: {str(e)}")
            
            # Create recovery context
            context = {
                'operation': agent.execute_task,
                'args': [task],
                'kwargs': {},
                'task': task,
                'agent_class': agent.__class__,
                'error': e
            }
            
            # Attempt recovery
            if self.recovery_manager.attempt_recovery(agent_id, e, context):
                logger.info(f"Successfully recovered from failure for agent {agent_id}")
                return {"status": "recovered", "message": "Task completed after recovery"}
            else:
                error_details = f"Failed to execute task: {str(e)}"
                logger.error(f"Recovery failed for agent {agent_id}: {error_details}")
                error_traceback = traceback.format_exc()
                raise AgentExecutionError(agent_id, task=task.get('type', 'unknown'), details=str(e))
    
    def execute_workflow(self, workflow_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a complete workflow with error handling and recovery.
        
        Args:
            workflow_id: ID of the workflow to execute
            context: Additional context for workflow execution
            
        Returns:
            Dict with workflow results or error information
            
        Raises:
            WorkflowException: If workflow execution fails
        """
        if workflow_id not in self.workflows:
            raise WorkflowException(f"Workflow {workflow_id} not found")
        
        workflow_steps = self.workflows[workflow_id]
        results = []
        context = context or {}
        
        try:
            for i, step in enumerate(workflow_steps):
                logger.info(f"Executing workflow {workflow_id} step {i+1}/{len(workflow_steps)}")
                
                agent_id = step.get('agent_id')
                if not agent_id:
                    raise WorkflowException(f"Missing agent_id in workflow step {i+1}")
                
                task = step.get('task', {})
                
                # Add workflow context to task
                task['workflow_context'] = context
                task['workflow_id'] = workflow_id
                task['step_index'] = i
                
                try:
                    step_result = self.execute_agent_task(agent_id, task)
                    results.append(step_result)
                    
                    # Update context with step results for subsequent steps
                    context.update({
                        f"step_{i}_result": step_result,
                        "last_step_result": step_result
                    })
                    
                    # Check if we need to stop workflow based on step result
                    if step.get('stop_on_condition') and self._evaluate_condition(
                        step['stop_on_condition'], step_result, context
                    ):
                        logger.info(f"Workflow {workflow_id} stopped at step {i+1} due to condition")
                        break
                        
                except AgentException as e:
                    logger.error(f"Agent failure in workflow {workflow_id} step {i+1}: {str(e)}")
                    
                    # Check if we can continue despite this error
                    if not step.get('continue_on_error', False):
                        raise WorkflowException(
                            f"Workflow {workflow_id} failed at step {i+1}: {str(e)}"
                        )
                    
                    logger.warning(f"Continuing workflow despite error in step {i+1}")
                    results.append({"status": "error", "message": str(e)})
                    
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "results": results,
                "context": context
            }
            
        except Exception as e:
            error_msg = f"Workflow {workflow_id} execution failed: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e),
                "partial_results": results,
                "context": context
            }
    
    def _evaluate_condition(self, condition: str, result: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition based on step result and context.
        
        Args:
            condition: String condition to evaluate
            result: Step result
            context: Current workflow context
            
        Returns:
            Boolean indicating if condition is met
        """
        try:
            # This is a simplified implementation
            # In a real implementation, you would want to use a safer
            # evaluation approach than eval()
            
            # Create a safe dictionary of variables for evaluation
            eval_locals = {
                "result": result,
                "context": context,
                "status": result.get("status"),
                "has_error": "error" in result or result.get("status") == "error",
            }
            
            return eval(condition, {"__builtins__": {}}, eval_locals)
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {str(e)}")
            return False

"""
Orchestrator with enhanced error handling capabilities.
"""
import logging
import time
import traceback
from typing import Any, Dict, List, Optional, Callable, Type, Union

# Import error handling modules
from cherry.core.errors import (
    CherryError, AgentError, AgentTimeoutError, AgentExecutionError, 
    OrchestratorError, MemoryError, ConfigurationError
)
from cherry.core.recovery import (
    retry, ErrorRecoveryHandler, ExponentialBackoff, ConstantRetry
)
from cherry.core.monitoring import ErrorMonitor

logger = logging.getLogger(__name__)

# ...existing code...

class Orchestrator:
    """
    Orchestrator that coordinates agents with robust error handling.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the orchestrator with configuration and error handling.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.agents = {}  # Map of agent_id to agent instance
        
        # Initialize error handling components
        self.error_recovery = ErrorRecoveryHandler(
            fallback_agents=self.config.get('fallback_agents', {})
        )
        self.error_monitor = ErrorMonitor()
        
        # Configure error thresholds
        self._configure_error_monitoring()
        
        # ...existing initialization code...
    
    def _configure_error_monitoring(self) -> None:
        """Configure error monitoring thresholds."""
        # Set default thresholds
        self.error_monitor.set_threshold("AgentTimeoutError", 5)
        self.error_monitor.set_threshold("AgentExecutionError", 10)
        
        # Apply custom thresholds from config if any
        custom_thresholds = self.config.get('error_thresholds', {})
        for error_type, threshold in custom_thresholds.items():
            self.error_monitor.set_threshold(error_type, threshold)
    
    def register_agent(self, agent_id: str, agent: Any, agent_type: Optional[str] = None) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent_id: Unique identifier for the agent
            agent: Agent instance
            agent_type: Type of agent for fallback purposes
        """
        try:
            if agent_id in self.agents:
                raise OrchestratorError(f"Agent with ID {agent_id} is already registered")
            
            self.agents[agent_id] = {
                'instance': agent,
                'type': agent_type,
                'status': 'idle',
                'last_error': None
            }
            logger.info(f"Agent {agent_id} registered successfully")
        except Exception as e:
            error_msg = f"Failed to register agent {agent_id}: {str(e)}"
            logger.error(error_msg)
            self.error_monitor.record_error("RegistrationError", error_msg)
            raise OrchestratorError(error_msg) from e
    
    @retry(max_attempts=3, retry_strategy=ExponentialBackoff(initial_delay=1.0))
    def execute_agent(self, agent_id: str, task: Any, timeout: float = 60.0) -> Any:
        """
        Execute a task with the specified agent, with error handling and timeout.
        
        Args:
            agent_id: ID of the agent to execute the task
            task: The task to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Result from the agent
            
        Raises:
            AgentError: If agent execution fails
            OrchestratorError: If agent is not registered
        """
        if agent_id not in self.agents:
            error_msg = f"Agent {agent_id} not registered"
            self.error_monitor.record_error("OrchestratorError", error_msg)
            raise OrchestratorError(error_msg)
        
        agent_info = self.agents[agent_id]
        agent = agent_info['instance']
        agent_info['status'] = 'busy'
        
        try:
            start_time = time.time()
            # Implement timeout mechanism
            # This is a simplified version - in a real implementation,
            # you might use threading or async mechanisms for proper timeouts
            result = agent.execute(task)  # Assume agent has an execute method
            
            execution_time = time.time() - start_time
            if execution_time > timeout:
                error_msg = f"Agent {agent_id} execution exceeded timeout of {timeout}s"
                self.error_monitor.record_error("AgentTimeoutError", error_msg)
                raise AgentTimeoutError(
                    message=error_msg,
                    timeout_seconds=timeout,
                    agent_id=agent_id,
                    agent_type=agent_info['type']
                )
            
            logger.debug(f"Agent {agent_id} completed task in {execution_time:.2f}s")
            return result
            
        except AgentError:
            # Re-raise agent errors directly
            raise
        except Exception as e:
            error_msg = f"Agent {agent_id} execution failed: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            self.error_monitor.record_error(
                "AgentExecutionError", 
                error_msg,
                {'agent_id': agent_id, 'agent_type': agent_info['type']}
            )
            
            # Create and raise a proper AgentExecutionError
            raise AgentExecutionError(
                message=error_msg,
                agent_id=agent_id,
                agent_type=agent_info['type'],
                original_exception=e
            ) from e
        finally:
            agent_info['status'] = 'idle'
    
    def execute_with_fallback(self, primary_agent_id: str, task: Any, timeout: float = 60.0) -> Any:
        """
        Execute a task with the primary agent, falling back to alternatives if it fails.
        
        Args:
            primary_agent_id: ID of the primary agent to use
            task: The task to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Result from successful agent execution
        """
        try:
            return self.execute_agent(primary_agent_id, task, timeout)
        except AgentError as e:
            logger.warning(f"Primary agent {primary_agent_id} failed, attempting recovery")
            try:
                return self.error_recovery.handle_agent_error(e, self)
            except Exception as recovery_error:
                logger.error(f"Recovery failed: {str(recovery_error)}")
                # Re-raise the original error if recovery fails
                raise e
    
    def execute_with_agent_type(self, agent_type: str, task: Any = None) -> Any:
        """
        Execute a task with the first available agent of the specified type.
        
        Args:
            agent_type: Type of agent to use
            task: The task to execute
            
        Returns:
            Result from agent execution
            
        Raises:
            OrchestratorError: If no agent of the specified type is available
        """
        # Find agents of the specified type
        matching_agents = [
            agent_id for agent_id, info in self.agents.items() 
            if info['type'] == agent_type and info['status'] == 'idle'
        ]
        
        if not matching_agents:
            error_msg = f"No available agents of type {agent_type}"
            self.error_monitor.record_error("OrchestratorError", error_msg)
            raise OrchestratorError(error_msg)
        
        # Use the first available agent
        return self.execute_agent(matching_agents[0], task)
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get the health status of the orchestrator and its agents.
        
        Returns:
            Dictionary with health status information
        """
        agent_status = {
            agent_id: {
                'status': info['status'],
                'type': info['type'],
                'last_error': info.get('last_error')
            }
            for agent_id, info in self.agents.items()
        }
        
        error_summary = self.error_monitor.get_error_summary()
        
        return {
            'status': 'healthy' if error_summary['total_errors'] < 5 else 'degraded',
            'agent_count': len(self.agents),
            'agents': agent_status,
            'errors': error_summary
        }
    
    def shutdown(self) -> None:
        """
        Shutdown the orchestrator gracefully.
        """
        logger.info("Shutting down orchestrator")
        # Export error logs before shutdown
        try:
            self.error_monitor.export_errors("orchestrator_errors.json")
        except Exception as e:
            logger.error(f"Failed to export error logs: {str(e)}")
        
        # Perform any necessary cleanup
        for agent_id, info in self.agents.items():
            try:
                # Assuming agents have a shutdown method
                if hasattr(info['instance'], 'shutdown'):
                    info['instance'].shutdown()
            except Exception as e:
                logger.error(f"Failed to shutdown agent {agent_id}: {str(e)}")
        
        logger.info("Orchestrator shutdown complete")

    # ...existing code...

from typing import Dict, List, Any, Optional, Type
import logging
from cherry.memory import MemoryManager
import importlib
import inspect

logger = logging.getLogger(__name__)

class Orchestrator:
    """Central orchestrator that coordinates agents and memory access."""
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.agents = {}
        self.available_agent_types = {}
        
    def register_agent_type(self, agent_type: str, agent_class):
        """Register an agent type for future instantiation."""
        self.available_agent_types[agent_type] = agent_class
        logger.info(f"Registered agent type: {agent_type}")
        
    def load_agent_types_from_directory(self, directory: str = "agents"):
        """Dynamically load agent types from a directory."""
        try:
            agents_module = importlib.import_module(directory)
            for name, obj in inspect.getmembers(agents_module):
                # Look for classes that have a process method and aren't the base class
                if inspect.isclass(obj) and hasattr(obj, 'process') and name != "BaseAgent":
                    self.register_agent_type(name.lower().replace("agent", ""), obj)
        except ImportError as e:
            logger.error(f"Failed to import agents module: {e}")
    
    def get_or_create_agent(self, agent_type: str) -> Any:
        """Get an existing agent instance or create a new one."""
        if agent_type not in self.agents:
            if agent_type not in self.available_agent_types:
                raise ValueError(f"Unknown agent type: {agent_type}")
                
            agent_class = self.available_agent_types[agent_type]
            self.agents[agent_type] = agent_class()
            logger.info(f"Created new agent of type: {agent_type}")
            
        return self.agents[agent_type]
    
    def determine_relevant_agents(self, request: Dict[str, Any]) -> List[str]:
        """Determine which agents are relevant for handling this request."""
        # This is a simplified example - in practice, use NLP or rules to determine relevance
        relevant_agents = []
        
        # Simple keyword matching for this demo
        if "research" in request["query"].lower() or "information" in request["query"].lower():
            relevant_agents.append("researcher")
            
        if "plan" in request["query"].lower() or "schedule" in request["query"].lower():
            relevant_agents.append("planner")
            
        # If no specific agents are identified, default to researcher
        if not relevant_agents:
            relevant_agents.append("researcher")
            
        return relevant_agents
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming request by coordinating agents and memory access."""
        query = request["query"]
        logger.info(f"Processing request: {query}")
        
        # Step 1: Retrieve relevant memories for this query
        memories = self.memory_manager.retrieve_memories(query)
        logger.info(f"Retrieved {len(memories)} memories")
        
        # Step 2: Determine which agents should handle this request
        relevant_agent_types = self.determine_relevant_agents(request)
        logger.info(f"Determined relevant agents: {relevant_agent_types}")
        
        # Step 3: Distribute memories to relevant agents and collect responses
        responses = {}
        for agent_type in relevant_agent_types:
            try:
                agent = self.get_or_create_agent(agent_type)
                
                # Filter memories relevant to this specific agent
                agent_memories = self.memory_manager.filter_memories_for_agent(memories, agent_type)
                
                # Process the request with the agent
                logger.info(f"Sending request to {agent_type} agent with {len(agent_memories)} memories")
                agent_response = agent.process(request, agent_memories)
                responses[agent_type] = agent_response
                
            except Exception as e:
                logger.error(f"Error with agent {agent_type}: {str(e)}")
                responses[agent_type] = {"error": str(e)}
                
        # Step 4: Combine responses (simple concatenation for this example)
        combined_response = self._combine_responses(responses)
        
        # Step 5: Store this interaction as a new memory
        self._store_interaction_as_memory(request, combined_response)
        
        return combined_response
    
    def _combine_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Combine responses from multiple agents into a single coherent response."""
        # Simple combination strategy - can be enhanced for better results
        combined_content = ""
        for agent_type, response in responses.items():
            if "error" in response:
                continue
            combined_content += f"\n\nFrom {agent_type}:\n{response['content']}"
            
        return {
            "content": combined_content.strip(),
            "agent_responses": responses
        }
    
    def _store_interaction_as_memory(self, request: Dict[str, Any], response: Dict[str, Any]):
        """Store the current interaction as a memory for future reference."""
        memory_content = f"Query: {request['query']}\nResponse: {response['content']}"
        self.memory_manager.store_memory(
            {
                "content": memory_content
            },
            metadata={
                "type": "interaction",
                "timestamp": request.get("timestamp", None)
            }
        )