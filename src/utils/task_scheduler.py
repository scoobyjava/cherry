"""
Task Scheduler for Cherry's autonomous development tasks.

This module provides functionality to prioritize and sequence development tasks
based on urgency, dependencies, and resource availability.
"""

import logging
import time
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime, timedelta
import heapq
from enum import Enum
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Status of a task in the scheduler."""
    PENDING = "pending"      # Task is waiting to be executed
    READY = "ready"          # Task is ready to be executed (dependencies met)
    RUNNING = "running"      # Task is currently running
    COMPLETED = "completed"  # Task has been completed successfully
    FAILED = "failed"        # Task failed during execution
    BLOCKED = "blocked"      # Task is blocked (dependencies not met)
    DEFERRED = "deferred"    # Task is temporarily deferred

class ResourceType(Enum):
    """Types of resources a task might require."""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    NETWORK = "network"
    DISK = "disk"
    API_QUOTA = "api_quota"

class Task:
    """Represents a development task with priority and dependencies."""
    
    def __init__(self, 
                 task_id: str, 
                 name: str, 
                 dependencies: List[str] = None, 
                 priority: int = 0, 
                 deadline: Optional[datetime] = None,
                 estimated_duration: Optional[int] = None,
                 resources: Dict[ResourceType, float] = None):
        """
        Initialize a new task.
        
        Args:
            task_id: Unique identifier for the task
            name: Descriptive name of the task
            dependencies: List of task IDs that must be completed before this task
            priority: Initial priority level (higher is more urgent)
            deadline: Optional deadline for task completion
            estimated_duration: Estimated time to complete in minutes
            resources: Dictionary of resource types and amounts required
        """
        self.task_id = task_id
        self.name = name
        self.dependencies = dependencies or []
        self.initial_priority = priority
        self.current_priority = priority
        self.deadline = deadline
        self.estimated_duration = estimated_duration
        self.resources = resources or {}
        self.status = TaskStatus.PENDING
        self.creation_time = datetime.now()
        self.start_time = None
        self.completion_time = None
        self.failure_reason = None
        self.attempts = 0
        self.max_attempts = 3
        
    def __lt__(self, other):
        """
        Compare tasks for priority queue ordering.
        Higher priority tasks come first, with deadline and creation time as tiebreakers.
        """
        if self.current_priority != other.current_priority:
            return self.current_priority > other.current_priority
            
        # If priorities match, check deadlines
        if self.deadline and other.deadline:
            return self.deadline < other.deadline
        elif self.deadline:
            return True  # Tasks with deadlines come before those without
        elif other.deadline:
            return False
            
        # If no deadlines or equal deadlines, older tasks come first
        return self.creation_time < other.creation_time
        
    def __str__(self):
        return (f"Task({self.task_id}: {self.name}, "
                f"priority={self.current_priority}, "
                f"status={self.status.value})")

    def time_until_deadline(self) -> Optional[timedelta]:
        """Return timedelta until deadline, or None if no deadline."""
        if not self.deadline:
            return None
        return self.deadline - datetime.now()
        
    def is_deadline_approaching(self, threshold_minutes: int = 60) -> bool:
        """Return True if deadline is within threshold_minutes."""
        time_left = self.time_until_deadline()
        if not time_left:
            return False
        return time_left.total_seconds() < threshold_minutes * 60
        
    def mark_as_running(self):
        """Mark task as running and record start time."""
        self.status = TaskStatus.RUNNING
        self.start_time = datetime.now()
        self.attempts += 1
        
    def mark_as_completed(self):
        """Mark task as completed and record completion time."""
        self.status = TaskStatus.COMPLETED
        self.completion_time = datetime.now()
        
    def mark_as_failed(self, reason: str = None):
        """Mark task as failed with optional reason."""
        self.failure_reason = reason
        
        if self.attempts >= self.max_attempts:
            self.status = TaskStatus.FAILED
            logger.warning(f"Task {self.task_id} failed after {self.attempts} attempts: {reason}")
        else:
            # Task can be retried
            self.status = TaskStatus.PENDING
            logger.info(f"Task {self.task_id} will be retried ({self.attempts}/{self.max_attempts})")


class TaskScheduler:
    """
    Scheduler for autonomous development tasks with dynamic prioritization.
    
    Features:
    - Dependency tracking to ensure proper execution order
    - Dynamic priority adjustment based on deadlines and other factors
    - Resource availability monitoring
    - Statistics on task execution and performance
    """
    
    def __init__(self):
        """Initialize a new task scheduler."""
        # Task storage
        self.tasks: Dict[str, Task] = {}
        
        # Priority queue for ready tasks
        self.ready_tasks = []
        
        # Dependency tracking
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)  # task -> dependent tasks
        self.remaining_dependencies: Dict[str, Set[str]] = defaultdict(set)  # task -> tasks it depends on
        
        # Resource tracking
        self.available_resources: Dict[ResourceType, float] = {
            ResourceType.CPU: 100.0,  # percent
            ResourceType.MEMORY: 100.0,  # percent
            ResourceType.GPU: 100.0,  # percent
            ResourceType.NETWORK: 100.0,  # percent
            ResourceType.DISK: 100.0,  # percent
            ResourceType.API_QUOTA: 100.0,  # percent
        }
        
        # Metrics
        self.completed_tasks_count = 0
        self.failed_tasks_count = 0
        self.avg_execution_time = 0.0
        
        # Last time priorities were recalculated
        self.last_priority_update = datetime.now()
        self.priority_update_interval = timedelta(minutes=5)
        
        logger.info("Task scheduler initialized")

    def add_task(self, task_name: str, dependencies: List[str] = None, priority: int = 0, 
                 deadline: Optional[datetime] = None, estimated_duration: Optional[int] = None,
                 resources: Dict[ResourceType, float] = None) -> str:
        """
        Add a new task to the scheduler.
        
        Args:
            task_name: Human-readable name for the task
            dependencies: List of task IDs that must complete before this task
            priority: Initial priority level (higher is more urgent)
            deadline: Optional deadline for completion
            estimated_duration: Estimated time to complete in minutes
            resources: Dictionary of resource types and amounts required
            
        Returns:
            task_id: Unique identifier for the added task
        """
        # Generate unique task ID
        task_id = f"task-{int(time.time() * 1000)}-{len(self.tasks)}"
        
        # Create the task
        task = Task(
            task_id=task_id,
            name=task_name,
            dependencies=dependencies or [],
            priority=priority,
            deadline=deadline,
            estimated_duration=estimated_duration,
            resources=resources
        )
        
        # Store the task
        self.tasks[task_id] = task
        
        # Set up dependency tracking
        remaining_deps = set()
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                logger.warning(f"Task {task_id} depends on unknown task {dep_id}")
                continue
                
            if self.tasks[dep_id].status != TaskStatus.COMPLETED:
                remaining_deps.add(dep_id)
                self.dependency_graph[dep_id].add(task_id)
        
        self.remaining_dependencies[task_id] = remaining_deps
        
        # If no dependencies, mark as ready and add to priority queue
        if not remaining_deps:
            task.status = TaskStatus.READY
            heapq.heappush(self.ready_tasks, task)
        else:
            task.status = TaskStatus.BLOCKED
            
        logger.info(f"Added task {task_id}: {task_name} with priority {priority}")
        return task_id
    
    def get_next_task(self) -> Optional[str]:
        """
        Get the next task to execute based on priority.
        
        Returns:
            task_id: ID of the highest priority ready task, or None if no tasks are ready
        """
        # Check if priority recalculation is needed
        self._check_update_priorities()
        
        # If no ready tasks, return None
        if not self.ready_tasks:
            return None
            
        # Get highest priority task
        task = heapq.heappop(self.ready_tasks)
        
        # Check if we have enough resources for this task
        if not self._has_sufficient_resources(task):
            # Put task back in queue and return None
            heapq.heappush(self.ready_tasks, task)
            logger.info(f"Task {task.task_id} deferred due to insufficient resources")
            return None
            
        # Mark task as running
        task.mark_as_running()
        
        logger.info(f"Selected task {task.task_id}: {task.name} (priority: {task.current_priority})")
        return task.task_id
    
    def complete_task(self, task_id: str, success: bool = True, failure_reason: str = None):
        """
        Mark a task as completed and update dependent tasks.
        
        Args:
            task_id: ID of the completed task
            success: Whether the task completed successfully
            failure_reason: Reason for failure if not successful
        """
        if task_id not in self.tasks:
            logger.error(f"Cannot complete unknown task {task_id}")
            return
            
        task = self.tasks[task_id]
        
        if success:
            task.mark_as_completed()
            self.completed_tasks_count += 1
            
            # Update execution time metrics
            if task.start_time and task.completion_time:
                execution_time = (task.completion_time - task.start_time).total_seconds()
                
                if self.avg_execution_time == 0:
                    self.avg_execution_time = execution_time
                else:
                    self.avg_execution_time = (self.avg_execution_time * (self.completed_tasks_count - 1) + 
                                              execution_time) / self.completed_tasks_count
            
            # Update dependent tasks
            for dependent_id in self.dependency_graph.get(task_id, set()):
                self.remaining_dependencies[dependent_id].remove(task_id)
                
                # If all dependencies are satisfied, mark as ready
                if not self.remaining_dependencies[dependent_id]:
                    dependent_task = self.tasks[dependent_id]
                    dependent_task.status = TaskStatus.READY
                    heapq.heappush(self.ready_tasks, dependent_task)
                    
            logger.info(f"Task {task_id} completed successfully")
        else:
            task.mark_as_failed(failure_reason)
            
            if task.status == TaskStatus.FAILED:
                self.failed_tasks_count += 1
            else:
                # Task will be retried, put back in queue
                heapq.heappush(self.ready_tasks, task)
                
            logger.info(f"Task {task_id} {'failed' if task.status == TaskStatus.FAILED else 'will be retried'}")
        
        # Release resources
        self._release_resources(task)
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the current status of a task."""
        if task_id not in self.tasks:
            return None
        return self.tasks[task_id].status
    
    def get_task_count_by_status(self) -> Dict[TaskStatus, int]:
        """Get count of tasks by status."""
        counts = {status: 0 for status in TaskStatus}
        for task in self.tasks.values():
            counts[task.status] += 1
        return counts
    
    def get_scheduler_stats(self) -> Dict[str, any]:
        """Get statistics about scheduler performance."""
        return {
            "total_tasks": len(self.tasks),
            "completed_tasks": self.completed_tasks_count,
            "failed_tasks": self.failed_tasks_count,
            "avg_execution_time": f"{self.avg_execution_time:.2f} seconds",
            "pending_tasks": len([t for t in self.tasks.values() if t.status in 
                                 (TaskStatus.PENDING, TaskStatus.READY, TaskStatus.BLOCKED)]),
            "ready_tasks": len(self.ready_tasks),
        }
        
    def _check_update_priorities(self):
        """
        Check if task priorities need to be recalculated and update if necessary.
        """
        now = datetime.now()
        if now - self.last_priority_update >= self.priority_update_interval:
            self._update_all_priorities()
            self.last_priority_update = now
    
    def _update_all_priorities(self):
        """Update priorities for all tasks based on various factors."""
        # Take out all ready tasks
        ready_tasks = self.ready_tasks.copy()
        self.ready_tasks = []
        
        for task in self.tasks.values():
            if task.status not in (TaskStatus.READY, TaskStatus.PENDING, TaskStatus.BLOCKED):
                continue
                
            # Start with the initial priority
            new_priority = task.initial_priority
            
            # Factor 1: Deadline proximity
            if task.deadline:
                time_left = task.time_until_deadline()
                if time_left:
                    # Adjust priority based on deadline proximity
                    hours_left = time_left.total_seconds() / 3600
                    if hours_left < 1:
                        # Less than an hour - huge boost
                        new_priority += 100
                    elif hours_left < 4:
                        # Less than 4 hours - significant
