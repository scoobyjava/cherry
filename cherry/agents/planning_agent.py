import os
import logging
import asyncio
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from cherry.agents.base_agent import Agent
import openai

logger = logging.getLogger(__name__)

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def ask_openai(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()


class PlanningAgent(Agent):
    """
    Agent that creates development plans, breaks down tasks,
    and helps estimate effort for software projects.
    """

    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.capabilities = [
            "planning", "task breakdown", "effort estimation",
            "dependency analysis", "project management", "roadmap creation"
        ]
        # Store common development tasks and their typical time requirements
        self._task_templates = {
            "feature implementation": {
                "small": {"min_days": 1, "max_days": 3},
                "medium": {"min_days": 3, "max_days": 7},
                "large": {"min_days": 7, "max_days": 15}
            },
            "bug fix": {
                "simple": {"min_days": 0.5, "max_days": 1},
                "complex": {"min_days": 1, "max_days": 5}
            },
            "documentation": {
                "standard": {"min_days": 1, "max_days": 2},
                "comprehensive": {"min_days": 3, "max_days": 7}
            },
            "refactoring": {
                "minor": {"min_days": 1, "max_days": 3},
                "major": {"min_days": 5, "max_days": 20}
            },
            "testing": {
                "unit": {"min_days": 1, "max_days": 3},
                "integration": {"min_days": 2, "max_days": 5},
                "end-to-end": {"min_days": 3, "max_days": 10}
            }
        }

    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a planning-related task.

        Args:
            task_data: Dictionary containing task details including:
                - task_type: Type of planning task (breakdown, estimation, roadmap)
                - project_path: Path to project directory (optional)
                - requirements: List of requirements or features to plan

        Returns:
            Dictionary containing planning results
        """
        logger.info(
            f"Running planning task: {task_data.get('task_type', 'general planning')}")

        # Extract task information
        task_type = task_data.get('task_type', 'breakdown')
        project_path = task_data.get('project_path', '')
        requirements = task_data.get('requirements', [])
        target_module = task_data.get('target_module', '')

        # Choose appropriate planning method based on task type
        if task_type == 'breakdown':
            return await self._create_task_breakdown(requirements, project_path, target_module)
        elif task_type == 'estimation':
            return await self._create_time_estimation(requirements)
        elif task_type == 'roadmap':
            return await self._create_project_roadmap(requirements, project_path)
        else:
            return {"error": f"Unknown planning task type: {task_type}"}

    async def _create_task_breakdown(self,
                                    requirements: List[str],
                                    project_path: str = "",
                                    target_module: str = "") -> Dict[str, Any]:
        """Break down requirements into actionable development tasks"""
        results = {
            "task_breakdown": [],
            "total_tasks": 0
        }

        try:
            # If target module is specified, analyze its structure
            module_analysis = {}
            if project_path and target_module:
                module_analysis = await self._analyze_module_structure(project_path, target_module)

            # Process each requirement
            for req_idx, requirement in enumerate(requirements):
                req_tasks = []

                # Basic tasks that almost always need to be done
                req_tasks.append({
                    "id": f"REQ{req_idx+1}-TASK1",
                    "name": f"Analyze requirements for {requirement}",
                    "description": "Review and clarify the requirement details",
                    "estimated_hours": 2
                })

                # If we have module analysis, use it to create more targeted tasks
                if module_analysis:
                    for component in module_analysis.get("components", []):
                        req_tasks.append({
                            "id": f"REQ{req_idx+1}-{component['name'].upper()}",
                            "name": f"Modify {component['name']} for {requirement}",
                            "description": f"Update the {component['name']} to implement the requirement",
                            "estimated_hours": self._estimate_component_work(component, requirement)
                        })
                else:
                    # Generic tasks if we don't have module analysis
                    req_tasks.extend([
                        {
                            "id": f"REQ{req_idx+1}-TASK2",
                            "name": f"Design implementation for {requirement}",
                            "description": "Create design document and technical approach",
                            "estimated_hours": 4,
                            "dependencies": [f"REQ{req_idx+1}-TASK1"]
                        },
                        {
                            "id": f"REQ{req_idx+1}-TASK3",
                            "name": f"Implement core functionality for {requirement}",
                            "description": "Code the main features needed to fulfill the requirement",
                            "estimated_hours": 8,
                            "dependencies": [f"REQ{req_idx+1}-TASK2"]
                        }
                    ])

                # Testing tasks are always needed
                req_tasks.extend([
                    {
                        "id":
