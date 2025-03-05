from typing import Dict, Any


def notify(recipient: str, from_agent: str, to_agent: str, explanation: str) -> None:
    # ...existing notification logic or integration...
    print(
        f"[Notification to {recipient}] Task handed off from {from_agent} to {to_agent}: {explanation}")


def pass_task(task_data: Dict[str, Any], from_agent: Any, to_agent: Any) -> None:
    """
    Passes a task from one agent to another.
    The originating agent provides an explanation if possible,
    and both Cherry and the user are notified upon handoff.
    """
    # Get explanation from the originating agent if available
    explanation_text = ""
    if hasattr(from_agent, "explain_task") and callable(from_agent.explain_task):
        explanation_text = from_agent.explain_task(task_data)
    else:
        explanation_text = f"Task '{task_data.get('id', 'unknown')}' handed off from {from_agent.name} to {to_agent.name}."

    # Notify Cherry and the user
    notify("Cherry", from_agent.name, to_agent.name, explanation_text)
    notify("User", from_agent.name, to_agent.name, explanation_text)

    # Hand off the task to the receiving agent
    if hasattr(to_agent, "receive_task") and callable(to_agent.receive_task):
        to_agent.receive_task(task_data)
    else:
        print(f"Error: {to_agent.name} cannot receive tasks.")
