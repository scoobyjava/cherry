import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentAchievements:
    """
    Tracks and manages achievements and metrics for Cherry agents.

    This class serves as a simple tracking mechanism for events that happen
    during agent execution, like tasks completed, coding proposals generated, etc.
    """

    def __init__(self):
        """Initialize the achievement tracker."""
        self._task_count = 0
        self._code_proposals = 0
        self._approved_proposals = 0
        self._achievements = []
        self._start_time = datetime.now()

    def record_task_completion(self, num_tasks: int = 1):
        """Record completion of tasks."""
        self._task_count += num_tasks

        # Check for milestones
        if self._task_count >= 100 and {"name": "Century", "description": "Completed 100 tasks"} not in self._achievements:
            self._achievements.append({
                "name": "Century",
                "description": "Completed 100 tasks",
                "date": datetime.now().isoformat()
            })
        elif self._task_count >= 50 and {"name": "Half-Century", "description": "Completed 50 tasks"} not in self._achievements:
            self._achievements.append({
                "name": "Half-Century",
                "description": "Completed 50 tasks",
                "date": datetime.now().isoformat()
            })
        elif self._task_count >= 10 and {"name": "Getting Started", "description": "Completed 10 tasks"} not in self._achievements:
            self._achievements.append({
                "name": "Getting Started",
                "description": "Completed 10 tasks",
                "date": datetime.now().isoformat()
            })

    def record_code_proposal(self):
        """Record generation of a code proposal."""
        self._code_proposals += 1

    def record_approved_proposal(self):
        """Record approval of a code proposal."""
        self._approved_proposals += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get current stats and achievements."""
        runtime = datetime.now() - self._start_time
        days = runtime.days
        hours, remainder = divmod(runtime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return {
            "tasks_completed": self._task_count,
            "code_proposals_generated": self._code_proposals,
            "code_proposals_approved": self._approved_proposals,
            "approval_rate": self._approved_proposals / self._code_proposals if self._code_proposals > 0 else 0,
            "uptime": f"{days}d {hours}h {minutes}m {seconds}s",
            "achievements": self._achievements
        }


# Singleton instance for global access
agent_achievements = AgentAchievements()
