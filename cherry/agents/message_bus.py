import asyncio
import logging

logger = logging.getLogger(__name__)

# Global dictionary for tracking agent performance scores
agent_scores = {}


async def message_bus(message: dict) -> dict:
    """
    Simulate sending a message to an agent.
    Message may include keys:
      - sender, recipient, type, payload.
    Returns a simulated acknowledgment.
    """
    logger.info(
        f"Message from {message.get('sender')} to {message.get('recipient')}: {message.get('type')}")
    await asyncio.sleep(0.1)  # simulate async processing delay
    return {"status": "delivered", "recipient": message.get("recipient")}


def dependency_checker(dep_graph: dict) -> bool:
    """
    Checks for circular dependencies in the provided dependency graph.
    Returns True if a cycle is detected.
    """
    visited = set()
    rec_stack = set()

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbour in dep_graph.get(node, []):
            if neighbour not in visited:
                if dfs(neighbour):
                    return True
            elif neighbour in rec_stack:
                return True
        rec_stack.remove(node)
        return False

    for node in dep_graph:
        if node not in visited:
            if dfs(node):
                logger.warning("Circular dependency detected.")
                return True
    return False


def update_agent_score(agent: str, score_delta: float) -> None:
    """
    Updates the performance score of an agent.
    """
    global agent_scores
    agent_scores[agent] = agent_scores.get(agent, 0) + score_delta
    logger.info(f"Updated score for {agent}: {agent_scores[agent]}")
