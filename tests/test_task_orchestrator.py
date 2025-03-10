import unittest
import time
from src.utils.task_orchestrator import TaskOrchestrator, TaskStatus


class TestTaskOrchestrator(unittest.TestCase):
    """Test case for the TaskOrchestrator class."""

    def test_sequential_execution(self):
        """Test that tasks are executed in the correct order."""
        orchestrator = TaskOrchestrator()

        # Create execution tracker
        execution_order = []

        # Define test functions
        def task1():
            execution_order.append("task1")
            return "Result from task1"

        def task2():
            execution_order.append("task2")
            return "Result from task2"

        def task3():
            execution_order.append("task3")
            return "Result from task3"

        # Add tasks with dependencies
        orchestrator.add_task("task1", "First task", task1, priority=2)
        orchestrator.add_task("task2", "Second task", task2, priority=1)
        orchestrator.add_task("task3", "Third task", task3,
                              dependencies=["task1", "task2"])

        # Run all tasks
        results = orchestrator.run_all_tasks()

        # Check execution order based on priority
        self.assertEqual(execution_order[0], "task2")  # Priority 1
        self.assertEqual(execution_order[1], "task1")  # Priority 2
        # Depends on task1 and task2
        self.assertEqual(execution_order[2], "task3")

        # Check that all tasks succeeded
        for task_id in ["task1", "task2", "task3"]:
            self.assertTrue(results[task_id].success)
            self.assertEqual(orchestrator.get_task_status(
                task_id), TaskStatus.COMPLETED)

    def test_error_handling(self):
        """Test that errors are properly handled and don't crash the orchestrator."""
        orchestrator = TaskOrchestrator()

        def failing_task():
            raise ValueError("This task intentionally fails")

        def dependent_task():
            return "This shouldn't run"

        orchestrator.add_task("failing", "A task that fails", failing_task)
        orchestrator.add_task("dependent", "Depends on failing task", dependent_task,
                              dependencies=["failing"])

        # Run all tasks
        results = orchestrator.run_all_tasks()

        # Check that the first task failed
        self.assertFalse(results["failing"].success)
        self.assertIsInstance(results["failing"].error, ValueError)
        self.assertEqual(orchestrator.get_task_status(
            "failing"), TaskStatus.FAILED)

        # Check that the dependent task was skipped
        self.assertFalse(results["dependent"].success)
        self.assertEqual(orchestrator.get_task_status(
            "dependent"), TaskStatus.SKIPPED)

    def test_parallel_execution(self):
        """Test that tasks can be executed in parallel."""
        orchestrator = TaskOrchestrator()

        # Create a task that takes some time
        def slow_task(task_name, duration):
            time.sleep(duration)
            return f"Completed {task_name}"

        # Add several independent tasks
        orchestrator.add_task("task1", "Task 1", slow_task,
                              task_name="task1", duration=0.5)
        orchestrator.add_task("task2", "Task 2", slow_task,
                              task_name="task2", duration=0.5)
        orchestrator.add_task("task3", "Task 3", slow_task,
                              task_name="task3", duration=0.5)

        # Time sequential execution
        orchestrator.reset()
        start_time = time.time()
        orchestrator.run_all_tasks(parallel=False)
        sequential_duration = time.time() - start_time

        # Time parallel execution
        orchestrator.reset()
        start_time = time.time()
        orchestrator.run_all_tasks(parallel=True)
        parallel_duration = time.time() - start_time

        # Parallel should be faster (allowing for some overhead)
        self.assertLess(parallel_duration, sequential_duration * 0.8)


if __name__ == '__main__':
    unittest.main()
