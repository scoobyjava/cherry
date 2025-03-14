import asyncio
import logging
import threading
import time
from typing import Dict, Any, List, Optional, Callable, Type, Union
from cherry.agents.base_agent import Agent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("cherry-orchestrator")

class UnifiedOrchestrator:
    """
    Central coordinator for Cherry's agent ecosystem.
    Manages agent interactions, workflows, and maintains system state.
    Supports both synchronous and asynchronous operation modes.
    """

    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the orchestrator with configuration.

        Args:
            config_path: Path to the configuration file
        """
        # Core state
        self.is_running = False
        self.task_queue = []
        self.completed_tasks = []
        self.lock = threading.RLock()
        self._thread = None
        self.loop = None

        # Agent management
        self.agents = {}
        self.max_concurrent_tasks = 3

        # Async specific
        self.async_task_queue = asyncio.Queue()
        self.approval_queue = []
        self.task_status = {}

        # Load configuration
        self.load_configuration(config_path)

        # Initialize memory system
        self._init_memory_system()

        logger.info("UnifiedOrchestrator initialized")

    def load_configuration(self, config_path: str):
        """Load configuration from the specified path."""
        try:
            # Configuration loading logic here
            logger.info(f"Configuration loaded from {config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Set default configuration
            pass

    def _init_memory_system(self):
        """Initialize the memory system for task tracking and history."""
        try:
            # Memory system initialization logic here
            logger.info("Memory system initialized")
        except Exception as e:
            logger.error(f"Memory initialization failed: {e}")

    def add_task(self, description: str, priority: int = 1, context: Optional[Dict[str, Any]] = None) -> int:
        """
        Add a task to the queue for processing.

        Args:
            description: Task description
            priority: Task priority (lower number = higher priority)
            context: Additional context for the task

        Returns:
            task_id: Unique identifier for the task
        """
        task_id = len(self.task_queue) + len(self.completed_tasks) + 1
        task = {
            "id": task_id,
            "description": description,
            "priority": priority,
            "status": "pending",
            "context": context or {},
            "created_at": time.time(),
            "dependencies": []
        }
        with self.lock:
            self.task_queue.append(task)
            # Sort by priority
            self.task_queue.sort(key=lambda t: t["priority"])

        logger.info(f"Task added: {task_id} - {description}")
        return task_id
    def _check_for_cycles(self):
        """Check for dependency cycles in the task queue."""
        visited = set()
        path = set()

        def visit(task):
            task_id = task["id"]
            if task_id in path:
                raise ValueError(f"Cycle detected in task dependencies involving task {task_id}")
            if task_id in visited:
                return

            visited.add(task_id)
            path.add(task_id)

            for dep_id in task.get("dependencies", []):
                dep_task = next((t for t in self.task_queue if t["id"] == dep_id), None)
                if dep_task:
                    visit(dep_task)

            path.remove(task_id)

        for task in self.task_queue:
            visit(task)

        logger.debug("No cycles detected in task dependencies")
    def get_task_status(self, task_id: int) -> Dict[str, Any]:
        """
        Get the status of a specific task.

        Args:
            task_id: The ID of the task to check

        Returns:
            Dict containing task status information
        """
        with self.lock:
            for task in self.task_queue + self.completed_tasks:
                if task["id"] == task_id:
                    return task
        return {"error": f"Task {task_id} not found"}

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all tasks (pending and completed).

        Returns:
            List of all tasks
        """
        with self.lock:
            return self.task_queue + self.completed_tasks

    def clear_completed_tasks(self):
        """Clear the list of completed tasks."""
        with self.lock:
            self.completed_tasks = []
        logger.info("Completed tasks cleared")

    def register_agent(self, agent: Agent) -> None:
        """
        Register an agent with the orchestrator.

        Args:
            agent: The agent to register
        """
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")

    def _select_agent_for_task(self, task: Dict[str, Any]) -> Optional[Agent]:
        """
        Select the most appropriate agent for a task.

        Args:
            task: The task to assign

        Returns:
            The selected agent or None if no suitable agent found
        """
        # Agent selection logic here
        # For now, return the first agent if any exist
        if self.agents:
            return next(iter(self.agents.values()))
        return None

    def can_execute_task(self, task: Dict[str, Any]) -> bool:
        """
        Check if a task can be executed (all dependencies satisfied).

        Args:
            task: The task to check

        Returns:
            True if the task can be executed, False otherwise
        """
        for dep_id in task.get("dependencies", []):
            dep_completed = any(t["id"] == dep_id and t["status"] == "completed" 
                               for t in self.completed_tasks)
            if not dep_completed:
                return False
        return True

    def process_with_agent(self, task: Dict[str, Any]):
        """
        Process a task using an appropriate agent.

        Args:
            task: The task to process
        """
        agent = self._select_agent_for_task(task)
        if agent:
            try:
                logger.info(f"Processing task {task['id']} with agent {agent.name}")
                # Update task status
                task["status"] = "in_progress"

                # Process task with agent
                result = agent.process_task(task)

                # Update task with result
                task["result"] = result
                task["status"] = "completed"
                task["completed_at"] = time.time()

                logger.info(f"Task {task['id']} completed successfully")
            except Exception as e:
                task["status"] = "failed"
                task["error"] = str(e)
                logger.error(f"Error processing task {task['id']}: {e}")
        else:
            task["status"] = "failed"
            task["error"] = "No suitable agent found"
            logger.error(f"No suitable agent found for task {task['id']}")

    # Synchronous execution methods
    def run(self):
        """Start the orchestrator in synchronous mode."""
        self.is_running = True
        logger.info("UnifiedOrchestrator started in synchronous mode")

        try:
            while self.is_running:
                executable_tasks = [task for task in self.task_queue if self.can_execute_task(task)]
                for task in executable_tasks:
                    self.process_with_agent(task)
                    with self.lock:
                        self.task_queue.remove(task)
                        self.completed_tasks.append(task)
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Orchestrator stopped by user")
        except Exception as e:
            logger.error(f"Error running orchestrator: {str(e)}")
        finally:
            self.is_running = False
            logger.info("UnifiedOrchestrator stopped")

    def start_background(self):
        """Start the orchestrator in a background thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("Orchestrator is already running")
            return

        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()
        logger.info("UnifiedOrchestrator started in background thread")
        return self

    def stop(self):
        """Stop the orchestrator."""
        self.is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        logger.info("UnifiedOrchestrator stopped")

    # Asynchronous execution methods
    async def _process_task_with_llm(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task using LLM capabilities.

        Args:
            task: The task to process

        Returns:
            The processed task with results
        """
        try:
            # LLM processing logic here
            task["status"] = "completed"
            task["completed_at"] = time.time()
            return task
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            logger.error(f"Error processing task with LLM: {e}")
            return {"error": str(e)}

    async def _task_consumer(self) -> None:
        """Asynchronous task consumer worker."""
        while self.is_running:
            try:
                task = await self.async_task_queue.get()

                # None is the signal to stop
                if task is None:
                    self.async_task_queue.task_done()
                    break

                logger.info(f"Processing task: {task.get('id', 'unknown')}")

                # Select agent for task
                agent = self._select_agent_for_task(task)

                if agent:
                    # Update task status
                    task["status"] = "in_progress"
                    self.task_status[task["id"]] = task

                    try:
                        # Process task with agent
                        result = await agent.async_process_task(task)

                        # Update task with result
                        task["result"] = result
                        task["status"] = "completed"
                        task["completed_at"] = time.time()

                        logger.info(f"Task {task['id']} completed successfully")
                    except Exception as e:
                        task["status"] = "failed"
                        task["error"] = str(e)
                        logger.error(f"Error processing task {task['id']}: {e}")
                else:
                    task["status"] = "failed"
                    task["error"] = "No suitable agent found"
                    logger.error(f"No suitable agent found for task {task['id']}")

                # Mark task as done
                self.async_task_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in task consumer: {e}")
                await asyncio.sleep(1)  # Prevent busy-waiting when errors occur

    async def start(self) -> None:
        """Start the orchestrator in asynchronous mode."""
        self.is_running = True
        logger.info("UnifiedOrchestrator started in asynchronous mode")

        # Start task consumer workers
        consumers = [
            asyncio.create_task(self._task_consumer())
            for _ in range(self.max_concurrent_tasks)
        ]

        # Wait for all consumers to complete (won't happen unless stop() is called)
        await asyncio.gather(*consumers)

    async def stop_async(self) -> None:
        """Stop the asynchronous orchestrator."""
        self.is_running = False

        # Signal all consumers to stop
        for _ in range(self.max_concurrent_tasks):
            await self.async_task_queue.put(None)

        logger.info("UnifiedOrchestrator async mode stopped")

    async def submit_task(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """
        Submit a task to the async queue.

        Args:
            task_type: Type of task
            task_data: Task data

        Returns:
            task_id: Unique identifier for the task
        """
        task_id = f"{task_type}-{time.time()}"
        task = {
            "id": task_id,
            "type": task_type,
            "data": task_data,
            "status": "pending",
            "created_at": time.time()
        }

        self.task_status[task_id] = task
        await self.async_task_queue.put(task)

        logger.info(f"Task submitted: {task_id}")
        return task_id

    async def get_async_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of an async task.

        Args:
            task_id: The ID of the task to check

        Returns:
            Dict containing task status information
        """
        if task_id in self.task_status:
            return self.task_status[task_id]
        return {"error": f"Task {task_id} not found"}

    async def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """
        Get all pending approval tasks.

        Returns:
            List of tasks pending approval
        """
        return self.approval_queue

    async def approve_change(self, task_id: str, approved: bool, feedback: str = "") -> Dict[str, Any]:
        """
        Approve or reject a pending change.

        Args:
            task_id: The ID of the task to approve/reject
            approved: Whether the change is approved
            feedback: Optional feedback

        Returns:
            Dict containing the result of the approval action
        """
        for i, task in enumerate(self.approval_queue):
            if task["id"] == task_id:
                task["approved"] = approved
                task["feedback"] = feedback

                # Remove from approval queue
                self.approval_queue.pop(i)

                if approved:
                    # Process the approved change
                    await self._process_approved_change(task)
                    return {"status": "approved", "task": task}
                else:
                    return {"status": "rejected", "task": task}

        return {"error": f"Task {task_id} not found in approval queue"}

    async def _process_approved_change(self, task: Dict[str, Any]) -> None:
        """
        Process an approved change.

        Args:
            task: The approved task to process
        """
        try:
            # Implementation logic for approved changes
            logger.info(f"Processing approved change for task {task['id']}")
            # Actual implementation would depend on the task type
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
