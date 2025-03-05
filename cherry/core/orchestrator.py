from cherry.agents.base_agent import Agent
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio
import json
import time
import networkx as nx
from threading import Lock
from typing import Dict, Any, List, Optional, Callable, Type, Union
from dataclasses import dataclass, field
import threading
import logging
import traceback
import importlib
import inspect

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
from .exceptions import (
    AgentException, AgentInitializationError, AgentExecutionError,
    OrchestratorException, WorkflowException, ResourceUnavailableException
)
from .recovery import RecoveryManager, RetryStrategy, FallbackAgentStrategy
from .errors import (
    CherryError, AgentError, AgentTimeoutError, OrchestratorError,
    MemoryError, ConfigurationError
)
from .monitoring import ErrorMonitor
from .recovery import retry, ErrorRecoveryHandler, ExponentialBackoff, ConstantRetry


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
            self.primary_memory = ChromaMemory(
                collection_name="cherry_primary_memory")
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
                logging.error(
                    f"Cycle detected: {task} is in the stack {stack}")
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
                    # Process tasks in FIFO order
                    task = self.task_queue.pop(0)
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


class MemoryInterface(ABC):
    @abstractmethod
    def store(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> str:
        """Store data in memory with optional namespace."""
        pass

    @abstractmethod
    def retrieve(self, query: str, namespace: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant memory entries based on semantic search."""
        pass

    @abstractmethod
    def update(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> bool:
        """Update an existing memory entry."""
        pass

    @abstractmethod
    def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        """Remove a memory entry."""
        pass


logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Central coordinator for Cherry's agent ecosystem.
    Manages agent interactions, workflows, and maintains system state.
    """

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.task_queue = asyncio.Queue()
        self.task_history: List[Dict[str, Any]] = []
        self.approval_queue: List[Dict[str, Any]] = []
        self.is_running = False
        self.max_concurrent_tasks = 3

    def register_agent(self, agent: Agent) -> None:
        """Register an agent with the orchestrator."""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")

    async def start(self) -> None:
        """Start the orchestrator and begin processing tasks."""
        self.is_running = True
        logger.info("Cherry orchestrator started")

        # Start task consumer workers
        consumers = [
            asyncio.create_task(self._task_consumer())
            for _ in range(self.max_concurrent_tasks)
        ]

        # Wait for all consumers to complete (won't happen unless stop() is called)
        await asyncio.gather(*consumers)

    async def stop(self) -> None:
        """Stop the orchestrator gracefully."""
        self.is_running = False
        logger.info("Cherry orchestrator stopping")

        # Add termination signals to the queue
        for _ in range(self.max_concurrent_tasks):
            await self.task_queue.put(None)

    async def submit_task(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """
        Submit a new task to be processed by the appropriate agent.

        Args:
            task_type: Type of task to be performed
            task_data: Data required for the task

        Returns:
            task_id: Unique identifier for tracking the task
        """
        task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.task_history)}"
        task = {
            "task_id": task_id,
            "task_type": task_type,
            "task_data": task_data,
            "status": "pending",
            "submitted_at": datetime.now().isoformat(),
            "requires_approval": task_data.get("requires_approval", False),
        }

        self.task_history.append(task)
        await self.task_queue.put(task)

        logger.info(f"Submitted task {task_id} of type {task_type}")
        return task_id

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the current status of a task."""
        for task in self.task_history:
            if task["task_id"] == task_id:
                return task
        return {"error": f"Task {task_id} not found"}

    async def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get list of changes waiting for user approval."""
        return self.approval_queue

    async def approve_change(self, task_id: str, approved: bool, feedback: str = "") -> Dict[str, Any]:
        """
        Approve or reject a proposed change.

        Args:
            task_id: ID of the task to approve
            approved: Whether the change is approved
            feedback: Optional feedback about the decision

        Returns:
            Updated task information
        """
        # Find the task in the approval queue
        for i, task in enumerate(self.approval_queue):
            if task["task_id"] == task_id:
                # Update task status
                task["status"] = "approved" if approved else "rejected"
                task["feedback"] = feedback
                task["decision_time"] = datetime.now().isoformat()

                # If approved, process the change
                if approved:
                    await self._process_approved_change(task)

                # Remove from approval queue
                self.approval_queue.pop(i)

                # Update task in history
                for hist_task in self.task_history:
                    if hist_task["task_id"] == task_id:
                        hist_task.update(task)
                        break

                return task

        return {"error": f"Task {task_id} not found in approval queue"}

    async def _task_consumer(self) -> None:
        """Background worker that processes tasks from the queue."""
        while self.is_running:
            task = await self.task_queue.get()

            # Check for termination signal
            if task is None:
                self.task_queue.task_done()
                break

            try:
                # Update task status
                task["status"] = "processing"
                task["started_at"] = datetime.now().isoformat()

                # Determine the appropriate agent
                agent = self._select_agent_for_task(task)
                if not agent:
                    task["status"] = "failed"
                    task["error"] = "No suitable agent found for this task"
                    continue

                # Process the task
                result = await agent.process(task["task_data"])

                # Check if this requires approval
                if task["requires_approval"]:
                    task["status"] = "awaiting_approval"
                    task["result"] = result
                    self.approval_queue.append(task)
                else:
                    task["status"] = "completed"
                    task["result"] = result

                task["completed_at"] = datetime.now().isoformat()

            except Exception as e:
                logger.error(f"Error processing task {task['task_id']}: {e}")
                task["status"] = "failed"
                task["error"] = str(e)
            finally:
                self.task_queue.task_done()

                # Update task in history
                for i, hist_task in enumerate(self.task_history):
                    if hist_task["task_id"] == task["task_id"]:
                        self.task_history[i] = task
                        break

    def _select_agent_for_task(self, task: Dict[str, Any]) -> Optional[Agent]:
        """Select the most appropriate agent for a given task."""
        task_type = task["task_type"]

        # Map task types to agent capabilities
        if task_type in ["planning", "breakdown", "estimation", "roadmap"]:
            for name, agent in self.agents.items():
                if "planning" in agent.capabilities:
                    return agent
        elif task_type in ["code_generation", "code_modification", "refactoring"]:
            for name, agent in self.agents.items():
                if "coding" in agent.capabilities:
                    return agent
        elif task_type in ["explain", "document", "summarize"]:
            for name, agent in self.agents.items():
                if "documentation" in agent.capabilities:
                    return agent

        # Default to the first agent that matches any capability
        for capability in task.get("task_data", {}).get("capabilities", []):
            for name, agent in self.agents.items():
                if capability in agent.capabilities:
                    return agent

        return None

    async def _process_approved_change(self, task: Dict[str, Any]) -> None:
        """Process a change that has been approved."""
        try:
            # Get the relevant coding agent
            coding_agent = None
            for name, agent in self.agents.items():
                if "coding" in agent.capabilities:
                    coding_agent = agent
                    break

            if not coding_agent:
                logger.error(
                    f"Cannot process approved change: no coding agent available")
                return

            # Prepare task data for implementation
            implementation_data = {
                "operation": "implement_approved_changes",
                "changes": task["result"]["changes"],
                "files": task["result"].get("files", []),
                "approved": True,
                "task_id": task["task_id"]
            }

            # Process the implementation
            result = await coding_agent.process(implementation_data)
            task["implementation_result"] = result

        except Exception as e:
            logger.error(
                f"Error implementing approved change {task['task_id']}: {e}")
            task["implementation_error"] = str(e)
