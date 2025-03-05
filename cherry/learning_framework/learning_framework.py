from cherry.learning_framework.solution_storage import VerifiedSolutionStorage


class LearningFramework:
    def __init__(self):
        self.storage = VerifiedSolutionStorage()

    def track_solution(self, task_signature: str, solution: str):
        """Record a verified solution."""
        self.storage.add_solution(task_signature, solution)

    def get_similar_solution(self, task_signature: str) -> str:
        """Return a similar solution if available."""
        similar = self.storage.find_similar(task_signature)
        return similar if similar else "No similar solution found."

    def adaptive_improvement(self, task_signature: str, execution_success: bool):
        """Update the stored solution based on execution result."""
        self.storage.update_solution(task_signature, execution_success)

# ...existing code or integration points...
