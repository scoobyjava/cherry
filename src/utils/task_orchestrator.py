"""
Task orchestration system for Cherry development workflows.
"""

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TaskOrchestrator")

class TaskStatus(Enum):
    """Enum representing the status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"  # For dependent tasks that can't run

@dataclass
class TaskResult:
    """Container for task execution results."""
    success: bool
    output: Any = None
    error: Optional[Exception] = None
    error_traceback: Optional[str] = None
    execution_time: float = 0.0

class Task:
    """Represents a single task in the orchestration system."""
    
    def __init__(self, 
                 task_id: str, 
                 description: str, 
                 action: Callable, 
                 priority: int = 1, 
                 dependencies: Optional[List[str]] = None,
                 **kwargs):
        """
        Initialize a new task.
        
        Args:
            task_id: Unique identifier for the task
            description: Human-readable description of the task
            action: Callable function that performs the task
            priority: Task priority (lower numbers execute first)
            dependencies: List of task_ids this task depends on
            **kwargs: Additional parameters to pass to the action
        """
        self.task_id = task_id
        self.description = description
        self.action = action
        self.priority = priority
        self.dependencies = dependencies or []
        self.kwargs = kwargs
        self.status = TaskStatus.PENDING
        self.result = None
        
    def __repr__(self):
        return f"Task({self.task_id}, priority={self.priority}, status={self.status.value})"

class TaskOrchestrator:
    """
    Manages and executes development tasks for Cherry.
    
    This class supports adding tasks with various properties,
    executing them in sequence or parallel, and tracking their status.
    """
    
    def __init__(self):
        """Initialize a new TaskOrchestrator."""
        self.tasks: Dict[str, Task] = {}
        self.results: Dict[str, TaskResult] = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        
    def add_task(self, 
                 task_id: str, 
                 description: str, 
                 action: Callable, 
                 priority: int = 1, 
                 dependencies: Optional[List[str]] = None,
                 **kwargs) -> None:
        """
        Add a task to the orchestrator.
        
        Args:
            task_id: Unique identifier for the task
            description: Human-readable description of the task
            action: Callable function that performs the task
            priority: Task priority (lower numbers execute first)
            dependencies: List of task_ids this task depends on
            **kwargs: Additional parameters to pass to the action
            
        Raises:
            ValueError: If a task with the same ID already exists
        """
        with self._lock:
            if task_id in self.tasks:
                raise ValueError(f"Task with ID '{task_id}' already exists")
            
            # Check for dependency existence
            if dependencies:
                for dep_id in dependencies:
                    if dep_id not in self.tasks and dep_id != task_id:
                        logger.warning(f"Task '{task_id}' depends on non-existent task '{dep_id}'")
            
            task = Task(task_id, description, action, priority, dependencies, **kwargs)
            self.tasks[task_id] = task
            logger.info(f"Added task: {task}")
    
    def run_task(self, task_id: str) -> TaskResult:
        """
        Run a specific task by its ID.
        
        Args:
            task_id: ID of the task to run
            
        Returns:
            TaskResult object containing execution results
            
        Raises:
            ValueError: If the task doesn't exist
        """
        with self._lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task '{task_id}' does not exist")
            
            task = self.tasks[task_id]
            
            # Check if dependencies are complete
            for dep_id in task.dependencies:
                if dep_id not in self.results or not self.results[dep_id].success:
                    error_msg = f"Cannot run task '{task_id}', dependency '{dep_id}' not completed"
                    logger.error(error_msg)
                    task.status = TaskStatus.SKIPPED
                    result = TaskResult(success=False, error=RuntimeError(error_msg))
                    self.results[task_id] = result
                    return result
        
        # Run the task (without holding the lock during execution)
        logger.info(f"Starting task: {task}")
        task.status = TaskStatus.IN_PROGRESS
        
        start_time = time.time()
        try:
            output = task.action(**task.kwargs)
            execution_time = time.time() - start_time
            result = TaskResult(success=True, output=output, execution_time=execution_time)
            
            with self._lock:
                task.status = TaskStatus.COMPLETED
                logger.info(f"Completed task: {task}, execution time: {execution_time:.2f}s")
        
        except Exception as e:
            execution_time = time.time() - start_time
            error_traceback = traceback.format_exc()
            result = TaskResult(
                success=False, 
                error=e, 
                error_traceback=error_traceback,
                execution_time=execution_time
            )
            
            with self._lock:
                task.status = TaskStatus.FAILED
                logger.error(f"Task '{task_id}' failed: {e}\n{error_traceback}")
        
        with self._lock:
            self.results[task_id] = result
            task.result = result
        
        return result
    
    def _get_runnable_tasks(self) -> List[str]:
        """
        Get a list of task IDs that can be run (dependencies satisfied).
        
        Returns:
            List of task IDs that are ready to run
        """
        runnable_tasks = []
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.PENDING:
                dependencies_met = True
                for dep_id in task.dependencies:
                    if dep_id not in self.results or not self.results[dep_id].success:
                        dependencies_met = False
                        break
                if dependencies_met:
                    runnable_tasks.append(task_id)
        
        # Sort by priority
        return sorted(runnable_tasks, key=lambda tid: self.tasks[tid].priority)
    
    def run_all_tasks(self, parallel: bool = False, max_workers: int = None) -> Dict[str, TaskResult]:
        """
        Run all pending tasks in the correct order.
        
        Args:
            parallel: If True, run tasks in parallel when possible
            max_workers: Maximum number of worker threads for parallel execution
            
        Returns:
            Dictionary mapping task IDs to their execution results
        """
        logger.info(f"Running all tasks (parallel={parallel})")
        
        if parallel:
            return self._run_parallel(max_workers)
        else:
            return self._run_sequential()
    
    def _run_sequential(self) -> Dict[str, TaskResult]:
        """Run all tasks sequentially."""
        while True:
            with self._lock:
                runnable_tasks = self._get_runnable_tasks()
                if not runnable_tasks:
                    break
            
            # Run the next task
            task_id = runnable_tasks[0]
            self.run_task(task_id)
        
        return self.results
    
    def _run_parallel(self, max_workers: int = None) -> Dict[str, TaskResult]:
        """Run tasks in parallel where dependencies allow."""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while True:
                with self._lock:
                    runnable_tasks = self._get_runnable_tasks()
                    if not runnable_tasks:
                        break
                
                # Submit all runnable tasks to the executor
                futures = {
                    executor.submit(self.run_task, task_id): task_id 
                    for task_id in runnable_tasks
                }
                
                # Wait for at least one task to complete
                for future in futures:
                    future.result()  # This will re-raise any exceptions
                    break
        
        return self.results
    
    def get_task_status(self, task_id: str) -> TaskStatus:
        """
        Get the current status of a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Current status of the task
            
        Raises:
            ValueError: If the task doesn't exist
        """
        with self._lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task '{task_id}' does not exist")
            return self.tasks[task_id].status
    
    def reset(self) -> None:
        """Reset all tasks to pending status and clear results."""
        with self._lock:
            for task in self.tasks.values():
                task.status = TaskStatus.PENDING
                task.result = None
            self.results.clear()
