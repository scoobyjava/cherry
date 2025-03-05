import os
import datetime
from typing import List, Dict, Any


async def request_new_agent(self, problem_description: str, capabilities: List[str] = None) -> str:
    """
    Dynamically request creation of a new agent to solve a specific problem.

    Args:
        problem_description: Description of the problem that needs solving.
        capabilities: Optional list of suggested capabilities.

    Returns:
        Request ID for tracking the new agent proposal.
    """
    from cherry.evolution.agent_factory import agent_request_handler

    # Generate a reasonable name based on the problem description
    name_words = [word for word in problem_description.lower().split()[:3]
                  if len(word) > 3 and word not in ['with', 'from', 'that', 'this', 'will']]
    name = "_".join(name_words) + "_agent" if name_words else "custom_agent"

    # Generate capabilities if none provided
    if not capabilities:
        capabilities = self._infer_capabilities_from_description(
            problem_description)

    # Submit a request – high priority for explicitly requested agents
    request_id = await agent_request_handler.request_new_agent(
        name=name,
        purpose=f"Solve problems related to: {problem_description}",
        problem_description=problem_description,
        capabilities=capabilities,
        priority=0.8
    )
    return request_id


def _infer_capabilities_from_description(self, description: str) -> List[str]:
    """
    Infer capabilities needed based on the problem description using keyword matching.
    Returns:
        A list of inferred capabilities.
    """
    capabilities = []
    # Simple keyword matching; a real system would leverage NLP techniques.
    keywords = {
        "data": ["data_processing", "analysis"],
        "analyze": ["analysis", "pattern_recognition"],
        "fast": ["optimization", "parallel_processing"],
        "parallel": ["parallel_processing"],
        "image": ["image_processing", "computer_vision"],
        "text": ["nlp", "text_processing"],
        "memory": ["memory_management", "caching"],
        "learn": ["machine_learning", "adaptation"],
        "adapt": ["adaptation", "learning"],
        "recommend": ["recommendation", "personalization"],
        "monitor": ["monitoring", "alerting"],
        "alert": ["alerting", "notification"],
        "schedule": ["scheduling", "time_management"],
        "search": ["search", "information_retrieval"],
        "retrieve": ["information_retrieval"],
        "translate": ["translation", "language_processing"],
        "secure": ["security", "encryption"],
        "encrypt": ["encryption", "security"]
    }

    description_lower = description.lower()
    for keyword, related_capabilities in keywords.items():
        if keyword in description_lower:
            capabilities.extend(related_capabilities)

    # Remove duplicates
    return list(set(capabilities))


async def evaluate_agent_performance(self, agent_name: str) -> Dict[str, Any]:
    """
    Request an evaluation of an agent's performance.

    Args:
        agent_name: Name of the agent to evaluate.

    Returns:
        Performance metrics and recommendations for the agent.
    """
    from cherry.feedback.system_evaluator import get_evaluator
    evaluator = get_evaluator()
    # Get performance metrics for the specified agent
    metrics = evaluator._analyze_agent_performance().get(agent_name, {})
    recommendations = []

    if metrics:
        if metrics.get("success_rate", 100) < 80:
            recommendations.append(
                "Consider revising task delegation or communication protocols.")
        if metrics.get("avg_response_time", 0) > 5:
            recommendations.append(
                "Explore optimizations for faster execution or parallelization.")
        if metrics.get("efficiency_score", 100) < 70:
            recommendations.append(
                "Enhance collaboration between agents for improved decision making.")
    else:
        recommendations.append("No performance data available for this agent.")

    return {
        "agent_name": agent_name,
        "metrics": metrics,
        "recommendations": recommendations
    }


async def propose_new_agent_blueprint(self, problem_description: str, capabilities: List[str]) -> Dict[str, Any]:
    """
    Generate a blueprint for a new agent based on the problem description and required capabilities.
    This simulates a Co-Pilot evaluation and design recommendation.

    Returns:
        A dictionary containing the proposed agent blueprint.
    """
    # For demonstration, we use a simple model. A full implementation could call an LLM.
    blueprint = {
        "name_suggestion": "_".join(problem_description.lower().split()[:3]) + "_agent",
        "capabilities": capabilities,
        "description": f"An agent designed to address: {problem_description}",
        "design": {
            "architecture": "microservice-based modular design",
            "communication": "asynchronous message passing using the existing message_bus",
            "fallback_strategy": "multi-layer fallback with runtime learning"
        },
        "integration": {
            "dependencies": ["message_bus", "system_evaluator"],
            "deployment": "dynamic registration with Cherry's orchestrator"
        }
    }
    return blueprint


async def deploy_new_agent(self, blueprint: Dict[str, Any]) -> str:
    """
    Deploy a newly blueprinted agent to Cherry's ecosystem after a trial phase.
    This function simulates a performance evaluation feedback loop before permanent integration.

    Returns:
        The name of the newly deployed agent.
    """
    # Simulate a trial deployment and evaluation cycle:
    trial_passed = True
    if trial_passed:
        # Here we would instantiate the new agent and register it.uld instantiate the new agent and register it.uld instantiate the new agent and register it.
        agent_name = blueprint.get("name_suggestion", "new_agent")
        # For instance, using an agent factory:
        from cherry.evolution.agent_factory import create_agent_from_blueprintort create_agent_from_blueprintort create_agent_from_blueprint
        new_agent = await create_agent_from_blueprint(blueprint)
        self.orchestrator.register_agent(agent_name, new_agent)
        return agent_name
    else:
        raise Exception(aise Exception(aise Exception(
            "Trial deployment failed. Agent design requires refinement.")yment failed. Agent design requires refinement.")yment failed. Agent design requires refinement.")
