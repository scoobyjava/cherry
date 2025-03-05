import os
import json
from difflib import SequenceMatcher

STORAGE_PATH = os.path.join(os.path.dirname(
    __file__), "verified_solutions.json")


def load_storage():
    if not os.path.exists(STORAGE_PATH):
        return {}
    with open(STORAGE_PATH, "r") as f:
        return json.load(f)


def save_storage(data):
    with open(STORAGE_PATH, "w") as f:
        json.dump(data, f, indent=2)


class VerifiedSolutionStorage:
    def __init__(self):
        self.solutions = load_storage()

    def add_solution(self, task_signature: str, solution: str):
        """Store a new verified solution."""
        self.solutions[task_signature] = {
            "solution": solution,
            "usage_count": 1
        }
        save_storage(self.solutions)

    def find_similar(self, task_signature: str, threshold: float = 0.7) -> str:
        """Return a similar solution if similarity ratio exceeds threshold."""
        best_match = None
        best_score = 0
        for sig, entry in self.solutions.items():
            score = SequenceMatcher(None, task_signature, sig).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_match = entry["solution"]
        return best_match

    def update_solution(self, task_signature: str, execution_result: bool):
        """Adapt stored solution based on execution result.
           If execution is successful, increase usage count; otherwise, decrease or remove.
        """
        if task_signature in self.solutions:
            if execution_result:
                self.solutions[task_signature]["usage_count"] += 1
            else:
                self.solutions[task_signature]["usage_count"] -= 1
                if self.solutions[task_signature]["usage_count"] <= 0:
                    del self.solutions[task_signature]
            save_storage(self.solutions)
