import asyncio
from cherry.agents.code_analysis_agent import CodeAnalysisAgent
from cherry.agents.planning_agent import PlanningAgent
from cherry.orchestration.agent_orchestrator import AgentOrchestrator

# Create specialized agents
code_agent = CodeAnalysisAgent("code_reviewer", "Analyzes code for issues and improvement opportunities")
planning_agent = PlanningAgent("project_planner", "Creates development plans and tasks")

# Create and configure the orchestrator
orchestrator = AgentOrchestrator()
orchestrator.register_agent(code_agent)
orchestrator.register_agent(planning_agent)

# Define a workflow
orchestrator.register_workflow(
    "code_improvement", 
    ["project_planner", "code_reviewer"]
)

# Example task execution
async def main():
    # Execute a single task
    result = await orchestrator.execute_task({
        "description": "Analyze performance of user authentication module",
        "code_path": "/path/to/auth_module.py"
    })
    print(f"Task result: {result}")
    
    # Execute a workflow
    workflow_result = await orchestrator.execute_workflow("code_improvement", {
        "project_path": "/path/to/project",
        "target_module": "authentication"
    })
    print(f"Workflow result: {workflow_result}")

# Run the example
if __name__ == "__main__":
    asyncio.run(main())