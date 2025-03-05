import json
import os
from collections import defaultdict
from datetime import datetime


class AssessmentTracker:
    def __init__(self, storage_file: str = "assessment_records.json"):
        # Initialize in-memory storage and load previous records if available
        self.storage_file = storage_file
        self.records = []
        if os.path.exists(storage_file):
            try:
                with open(storage_file, 'r') as f:
                    self.records = json.load(f)
            except Exception:
                self.records = []

    def log_assessment(self, task_type: str, model: str, outcome: str, feedback: str):
        """
        Log an assessment record.
        outcome: "success" or "failure"
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "model": model,
            "outcome": outcome,
            "feedback": feedback
        }
        self.records.append(record)
        self._persist_records()

    def _persist_records(self):
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.records, f, indent=2)
        except Exception as e:
            print(f"Error persisting records: {e}")

    def compute_metrics(self):
        """
        Calculate success rate per model and task type.
        Returns a dictionary with structure:
        {
            "models": { model_name: { "success": int, "failure": int, "success_rate": float } },
            "tasks": { task_type: { "success": int, "failure": int, "success_rate": float } }
        }
        """
        model_stats = defaultdict(lambda: {"success": 0, "failure": 0})
        task_stats = defaultdict(lambda: {"success": 0, "failure": 0})
        for rec in self.records:
            outcome = rec.get("outcome", "").lower()
            model = rec.get("model")
            task_type = rec.get("task_type")
            if outcome == "success":
                model_stats[model]["success"] += 1
                task_stats[task_type]["success"] += 1
            else:
                model_stats[model]["failure"] += 1
                task_stats[task_type]["failure"] += 1

        # Compute success rates
        def calc_rate(stats):
            total = stats["success"] + stats["failure"]
            rate = (stats["success"] / total) if total > 0 else 0.0
            stats["success_rate"] = rate
            return stats

        models = {model: calc_rate(stats)
                  for model, stats in model_stats.items()}
        tasks = {task: calc_rate(stats) for task, stats in task_stats.items()}

        return {"models": models, "tasks": tasks}

    def analyze_performance(self):
        """
        Analyze performance trends and provide suggestions.
        Returns a dictionary with recommendations keyed by task type.
        """
        metrics = self.compute_metrics()
        recommendations = {}
        for task, stats in metrics["tasks"].items():
            # Recommend reviewing model choice for tasks with low success rate
            if stats["success_rate"] < 0.7:
                recommendations[task] = (
                    f"Task '{task}' has a low success rate ({stats['success_rate']:.0%}). "
                    "Consider re-evaluating the model selection or adjusting task breakdown."
                )
            else:
                recommendations[task] = f"Task '{task}' performs well ({stats['success_rate']:.0%} success rate)."
        return recommendations

    def suggest_improvements(self):
        """
        Provides an overall suggestion based on performance metrics.
        """
        metrics = self.compute_metrics()
        overall_success = sum(stat["success"]
                              for stat in metrics["tasks"].values())
        overall_fail = sum(stat["failure"]
                           for stat in metrics["tasks"].values())
        total = overall_success + overall_fail

        if total == 0:
            return "No assessments logged yet. Unable to analyze performance."

        overall_rate = overall_success / total
        if overall_rate < 0.75:
            return (
                f"Overall success rate is {overall_rate:.0%}. Consider revisiting the selection criteria "
                "for models to improve performance."
            )
        else:
            return f"Overall performance is satisfactory with a {overall_rate:.0%} success rate."


# ... Code for exposing a singleton tracker if needed ...
tracker = AssessmentTracker()
