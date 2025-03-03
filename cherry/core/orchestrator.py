import asyncio
import json
import time
import networkx as nx
from threading import Lock
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

import openai
from config import Config
from logger import logger
from memory_chroma import ChromaMemory

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
            return task_id

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