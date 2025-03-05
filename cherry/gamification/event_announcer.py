import logging

logger = logging.getLogger(__name__)

def check_task_streak(agent_name: str, task_history: list) -> None:
    """
    Checks if the agent has completed 3 tasks in a row without delegate delays.
    If yes, logs a fun announcement.
    """
    # A simple check: last 3 tasks should be marked complete without delay flag.
    if len(task_history) < 3:
        return

    # Assume each task is a dict with keys: 'completed' (bool) and 'delegate_delay' (bool)
    last_three = task_history[-3:]
    if all(task.get("completed", False) and not task.get("delegate_delay", False) for task in last_three):
        logger.info(f"Cherry announces: Agent {agent_name} just completed 3 tasks in a row without delegate delays!")
