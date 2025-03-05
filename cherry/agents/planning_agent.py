from cherry.agents.message_bus import message_bus, dependency_checker, update_agent_score
import os
import logging
import asyncio
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from cherry.agents.base_agent import Agent
import openai
import random

logger = logging.getLogger(__name__)

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logger.critical("OPENAI_API_KEY environment variable not set")


async def ask_openai(prompt):
    """Ask OpenAI API for a completion based on the prompt."""
    if not openai.api_key:
        logger.error("OPENAI_API_KEY environment variable must be set")
        return "Error: API key not set"

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in OpenAI API call: {e}")
        return f"Error generating response: {str(e)}"


def select_model_for_task(task_description: str) -> str:
    """
    Selects an appropriate model based on the task description.

    Mappings:
    - Tasks involving reasoning or conceptual problems use 'gpt-4'.
    - Tasks involving refactoring, debugging, or syntax modifications use Codex (e.g., 'code-davinci-002').
    - Tasks involving performance testing or optimization use 'gpt-3.5-turbo'.

    Includes fallback logic if the primary model check fails.
    """
    logger.info(f"Selecting model for task: {task_description}")
    lower_desc = task_description.lower()

    if "refactor" in lower_desc or "syntax" in lower_desc or "debug" in lower_desc or "bug" in lower_desc:
        model = "code-davinci-002"  # Codex
    elif "performance" in lower_desc or "optimization" in lower_desc:
        model = "gpt-3.5-turbo"
    elif "conceptual" in lower_desc or "reasoning" in lower_desc:
        model = "gpt-4"
    else:
        model = "gpt-4"  # Default choice

    logger.info(f"Primary model chosen: {model}")

    # Fallback logic: simulate model availability check
    try:
        # ...simulate a test call to check model availability...
        # For instance, you might call openai.Model.retrieve(model)
        pass
    except Exception as e:
        fallback = "gpt-4"  # Fallback default
        logger.error(
            f"Primary model {model} failed due to: {e}. Falling back to {fallback}")
        model = fallback

    logger.info(f"Final model selection: {model}")
    return model


class PlanningAgent(Agent):
    """
    Agent that creates development plans, breaks down tasks,
    and helps estimate effort for software projects.

    This agent provides capabilities for:
    - Breaking down requirements into actionable tasks
    - Estimating development time for features and projects
    - Creating project roadmaps with milestones
    - Scheduling and prioritizing tasks based on complexity and deadlines
    - Self-diagnosing performance issues

    The planning is based on templates and heuristics which can be customized
    for specific project types and team capabilities.
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
        # New: Dictionary to track task feedback history
        self.task_feedback_history = {}

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
            result = await self._create_task_breakdown(requirements, project_path, target_module)
            from cherry.agents.agent_achievements import agent_achievements
            agent_achievements.record_task_completion(
                result.get("total_tasks", 0))
            return result
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
                        "id": f"REQ{req_idx+1}-TASK4",
                        "name": f"Write unit tests for {requirement}",
                        "description": "Create unit tests to verify the requirement",
                        "estimated_hours": 3,
                        "dependencies": [f"REQ{req_idx+1}-TASK3"]
                    },
                    {
                        "id": f"REQ{req_idx+1}-TASK5",
                        "name": f"Perform integration testing for {requirement}",
                        "description": "Ensure the requirement works well with other components",
                        "estimated_hours": 4,
                        "dependencies": [f"REQ{req_idx+1}-TASK4"]
                    }
                ])

                results["task_breakdown"].append({
                    "requirement": requirement,
                    "tasks": req_tasks
                })
                results["total_tasks"] += len(req_tasks)

        except Exception as e:
            logger.error(f"Error creating task breakdown: {e}")
            results["error"] = str(e)

        return results

    async def _create_time_estimation(self, requirements: List[str]) -> Dict[str, Any]:
        """Estimate time required to complete given requirements"""
        results = {
            "time_estimation": [],
            "total_estimated_days": 0
        }

        try:
            # Estimate time for each requirement
            for requirement in requirements:
                est_days = self._estimate_requirement_time(requirement)
                results["time_estimation"].append({
                    "requirement": requirement,
                    "estimated_days": est_days
                })
                results["total_estimated_days"] += est_days

        except Exception as e:
            logger.error(f"Error creating time estimation: {e}")
            results["error"] = str(e)

        return results

    async def _create_project_roadmap(self, requirements: List[str], project_path: str) -> Dict[str, Any]:
        """Create a high-level project roadmap based on requirements"""
        results = {
            "roadmap": [],
            "total_duration_days": 0
        }

        try:
            # Analyze project structure if path is provided
            project_analysis = {}
            if project_path:
                project_analysis = await self._analyze_project_structure(project_path)

            # Create roadmap entries for each requirement
            for requirement in requirements:
                roadmap_entry = {
                    "requirement": requirement,
                    "milestones": []
                }

                # Add milestones based on project analysis
                if project_analysis:
                    for phase in project_analysis.get("phases", []):
                        roadmap_entry["milestones"].append({
                            "phase": phase["name"],
                            "description": f"Complete {phase['name']} for {requirement}",
                            "estimated_days": self._estimate_phase_time(phase, requirement)
                        })
                else:
                    # Generic milestones if no project analysis
                    roadmap_entry["milestones"].extend([
                        {
                            "phase": "Design",
                            "description": f"Design the solution for {requirement}",
                            "estimated_days": 5
                        },
                        {
                            "phase": "Implementation",
                            "description": f"Implement the solution for {requirement}",
                            "estimated_days": 10
                        },
                        {
                            "phase": "Testing",
                            "description": f"Test the solution for {requirement}",
                            "estimated_days": 7
                        }
                    ])

                results["roadmap"].append(roadmap_entry)
                results["total_duration_days"] += sum(
                    milestone["estimated_days"] for milestone in roadmap_entry["milestones"]
                )

        except Exception as e:
            logger.error(f"Error creating project roadmap: {e}")
            results["error"] = str(e)

        return results

    async def generate_personalized_response(self, task_update: str) -> str:
        """
        Generate a personalized response using GPT-4 with a predefined personality style.
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a friendly, slightly humorous assistant who provides insightful commentary."},
                    {"role": "user", "content": f"Task update: {task_update}\nRespond with personality:"}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except asyncio.TimeoutError:
            logger.error("OpenAI API request timed out")
            return "Sorry, the response timed out. Please try again."
        except Exception as e:
            logger.error(f"Error generating personalized response: {e}")
            return "Sorry, there was an error generating the response."

    def schedule_task(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Dynamically adjust task priorities based on complexity and deadlines.

        Each task must include:
          - 'complexity': an integer (>= 1)
          - 'deadline': an ISO formatted datetime string

        Returns:
          - Tasks sorted in descending order by computed priority_score.
        """
        w_deadline = 0.6
        w_complexity = 0.4
        now = datetime.now()
        scheduled_tasks = []

        for task in tasks:
            # Parse deadline from ISO string
            deadline = datetime.fromisoformat(task['deadline'])
            # Calculate time left in hours; if past, assign a minimal threshold
            time_left = (deadline - now).total_seconds() / 3600
            urgency = 1 / (time_left if time_left > 0 else 0.1)
            # Lower complexity gets a higher score (assumes complexity >= 1)
            difficulty = 1 / task.get('complexity', 1)

            task['priority_score'] = w_deadline * \
                urgency + w_complexity * difficulty
            scheduled_tasks.append(task)

        # Sort tasks: higher priority_score comes first
        scheduled_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
        return scheduled_tasks

    async def perform_self_diagnosis(self) -> Dict[str, Any]:
        """
        Perform proactive self-diagnosis with real-time monitoring,
        automated troubleshooting, and predictive maintenance.
        """
        diagnosis = {}
        diagnosis['timestamp'] = datetime.now().isoformat()
        diagnosis['system_load'] = os.getloadavg(
        ) if hasattr(os, 'getloadavg') else "N/A"
        diagnosis['task_queue_length'] = len(
            self._task_templates)  # placeholder metric
        diagnosis['inefficiencies'] = self._analyze_efficiencies()
        diagnosis['troubleshooting'] = self._automated_troubleshooting(
            diagnosis)
        diagnosis['predictive_maintenance'] = self._predictive_maintenance(
            diagnosis)

        return diagnosis

    def _analyze_efficiencies(self) -> List[str]:
        """
        Analyze internal data to identify inefficiencies.
        Returns a list of inefficiency descriptions.
        """
        inefficiencies = []

        # Check for excessive task templates
        if len(self._task_templates) > 5:  # arbitrary condition for demo
            inefficiencies.append(
                "Too many task templates; consider consolidating similar tasks.")

        # Check for wide estimation ranges
        for category, times in self._task_templates.items():
            for size, time in times.items():
                range_size = time["max_days"] - time["min_days"]
                if range_size > 10:
                    inefficiencies.append(
                        f"Wide estimation range for {category}/{size}; consider refining estimates.")

        return inefficiencies

    def _automated_troubleshooting(self, diagnosis: Dict[str, Any]) -> List[str]:
        """
        Provide troubleshooting suggestions based on diagnosis.
        """
        suggestions = []

        # System load checks
        if diagnosis.get("system_load") != "N/A" and diagnosis["system_load"][0] > 1.0:
            suggestions.append(
                "High system load detected; consider load balancing.")

        # Inefficiency checks
        inefficiencies = diagnosis.get("inefficiencies", [])
        if not inefficiencies:
            suggestions.append(
                "No inefficiencies detected. System operating normally.")
        else:
            for issue in inefficiencies:
                suggestions.append(f"Optimization opportunity: {issue}")

        # Queue length checks
        queue_length = diagnosis.get("task_queue_length", 0)
        if queue_length > 10:
            suggestions.append(
                f"Task queue length ({queue_length}) is high; consider scaling resources.")

        return suggestions

    def _predictive_maintenance(self, diagnosis: Dict[str, Any]) -> str:
        """
        Offer a predictive maintenance recommendation based on diagnosis.
        """
        # System load analysis
        if diagnosis.get("system_load") != "N/A":
            load = diagnosis["system_load"]
            if isinstance(load, tuple) and len(load) > 0:
                if load[0] > 1.5:
                    return "Schedule maintenance to check system performance within 24 hours."
                elif load[0] > 1.0:
                    return "Schedule routine maintenance within the next week."

        # Check for inefficiencies threshold
        if len(diagnosis.get("inefficiencies", [])) > 3:
            return "System optimization recommended within the next 3 days."

        # Check task queue health
        if diagnosis.get("task_queue_length", 0) > 15:
            return "Queue optimization maintenance recommended."

        return "Maintenance not required at this moment."

    async def _analyze_module_structure(self, project_path: str, target_module: str) -> Dict[str, Any]:
        """Analyze the structure of a specific module in the project"""
        components = []
        try:
            module_path = os.path.join(project_path, target_module)
            if os.path.exists(module_path):
                # Simple component detection based on files
                for root, dirs, files in os.walk(module_path):
                    for file in files:
                        if file.endswith('.py') and not file.startswith('__'):
                            components.append({
                                "name": os.path.splitext(file)[0],
                                "path": os.path.join(root, file),
                                "complexity": self._estimate_file_complexity(os.path.join(root, file))
                            })
                return {"components": components}
        except Exception as e:
            logger.error(f"Error analyzing module structure: {e}")
            return {"components": [], "error": str(e)}

    async def _analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Analyze the overall structure of a project for roadmap planning"""
        if not project_path or not os.path.exists(project_path):
            return {"phases": []}

        # Default phases if we can't determine from project
        phases = [
            {"name": "Design", "weight": 0.2},
            {"name": "Implementation", "weight": 0.5},
            {"name": "Testing", "weight": 0.2},
            {"name": "Deployment", "weight": 0.1}
        ]

        try:
            # Look for project structure indicators
            has_tests = False
            has_docs = False
            has_ci = False

            # Check for test directory
            if os.path.exists(os.path.join(project_path, 'tests')):
                has_tests = True

            # Check for docs directory
            if os.path.exists(os.path.join(project_path, 'docs')):
                has_docs = True

            # Check for CI configuration files
            ci_files = ['.github/workflows', '.travis.yml',
                        'Jenkinsfile', '.gitlab-ci.yml']
            for ci_file in ci_files:
                if os.path.exists(os.path.join(project_path, ci_file)):
                    has_ci = True
                    break

            # Adjust phases based on project structure
            if has_docs:
                phases.append({"name": "Documentation", "weight": 0.15})

            if has_ci:
                phases.append({"name": "CI/CD Setup", "weight": 0.1})

            return {"phases": phases}
        except Exception as e:
            logger.error(f"Error analyzing project structure: {e}")
            return {"phases": phases, "error": str(e)}

    def _estimate_component_work(self, component: Dict[str, Any], requirement: str) -> float:
        """Estimate work hours needed for a component based on complexity"""
        base_hours = 2.0  # Minimum hours
        # Adjust hours based on complexity
        if "complexity" in component:
            return base_hours * component["complexity"]
        return base_hours

    def _estimate_file_complexity(self, file_path: str) -> float:
        """Estimate complexity of a file based on its content"""
        try:
            if not os.path.exists(file_path):
                return 1.0

            with open(file_path, 'r') as f:
                content = f.read()

            # Simple complexity heuristics
            lines = content.count('\n') + 1
            classes = content.count('class ')
            functions = content.count('def ')

            # Calculate complexity score
            complexity = 1.0
            if lines > 500:
                complexity += 1.0
            if classes > 5:
                complexity += 0.5
            if functions > 10:
                complexity += 0.5

            return complexity
        except Exception:
            # Default complexity if analysis fails
            return 1.0

    def _estimate_requirement_time(self, requirement: str) -> float:
        """Estimate time needed to implement a requirement"""
        # Use task templates as basis for estimation
        est_days = 3.0  # Default estimate
        words = requirement.lower().split()

        # Adjust based on keywords
        if any(word in words for word in ['simple', 'minor', 'small']):
            est_days = 2.0
        elif any(word in words for word in ['complex', 'major', 'large']):
            est_days = 7.0

        return est_days

    def _estimate_phase_time(self, phase: Dict[str, Any], requirement: str) -> float:
        """Estimate time needed for a specific phase"""
        phase_name = phase.get("name", "").lower()
        if phase_name == "design":
            return 3.0
        elif phase_name == "implementation":
            return 5.0
        elif phase_name == "testing":
            return 2.0
        else:
            return 4.0  # Default

    async def rephrase_proposal(self, rejected_proposal: str, feedback: str) -> str:
        """
        Rephrase a rejected proposal based on user feedback to generate a better alternative.
        """
        try:
            prompt = (
                f"Original Proposal: {rejected_proposal}\n"
                f"User Feedback: {feedback}\n"
                "Please provide an improved version of the proposal based on the feedback."
            )
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            new_proposal = response.choices[0].message.content.strip()
            if not new_proposal:
                return "Fallback: Please consider revising the proposal manually using your feedback."
            return new_proposal
        except Exception as e:
            logger.error(f"Error rephrasing proposal: {e}")
            return "Fallback: Unable to generate a rephrased proposal. Please review the feedback and adjust the proposal manually."

    async def dynamic_rephrase_prompt(self, blocked_prompt: str) -> str:
        """
        Dynamically rephrase a blocked prompt to remove content that conflicts with public content rules.

        Steps:
        1. Analyze the prompt to detect patterns (e.g., "line 42") and replace them.
        2. Log both original and updated prompts for learning improvements.
        3. Retry the updated prompt using Co-Pilot (gpt-4) for a new response.
        """
        import re
        # Analyze: remove references like "line <number>"
        updated_prompt = re.sub(
            r'(line\s*\d+)', 'the appropriate code sections', blocked_prompt, flags=re.IGNORECASE)
        # Log original and updated prompt
        logger.info(
            f"Dynamic rephrase: Original Prompt: {blocked_prompt} | Updated Prompt: {updated_prompt}")
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[{"role": "user", "content": updated_prompt}],
                max_tokens=150
            )
            rephrased = response.choices[0].message.content.strip()
            logger.info("Dynamic rephrase successful.")
            return rephrased
        except Exception as e:
            logger.error(f"Dynamic rephrase failed: {e}")
            return "Fallback: Rephrasing failed, please review the prompt manually."

    async def generate_deployment_suggestions(self) -> str:
        """
        Generate deployment suggestions using Copilot. If suggestions are invalid or generation fails,
        provide manual deployment steps or a retry mechanism to gather new data.
        """
        try:
            prompt = "Provide detailed deployment suggestions for the current project setup."
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            suggestion = response.choices[0].message.content.strip()
            # Validate suggestion; fallback if too short or empty
            if len(suggestion) < 20:
                raise ValueError("Invalid suggestion length")
            return suggestion
        except Exception as e:
            logger.error(f"Error generating deployment suggestion: {e}")
            fallback_steps = (
                "Manual Deployment Steps:\n"
                "1. Verify the project configuration files.\n"
                "2. Ensure all dependencies are installed correctly.\n"
                "3. Deploy using your preferred deployment tool or script.\n"
                "If issues persist, please provide additional data for further troubleshooting."
            )
            return fallback_steps

    async def run_assessment_with_model(self, task_description: str, model_selection: str, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform an assessment using Copilot with the chosen model.
        Args:
            task_description: Description of the task.
            model_selection: Model details (e.g. "gpt-4", "code-davinci-002").
            task_params: Task-specific parameters.
        Returns:
            Dict with keys: "success", "metrics", "errors", "deployment_recommendations".
        """
        logger.info(
            f"Starting assessment with model {model_selection} for task: {task_description}")
        try:
            prompt = (
                f"Task Description: {task_description}\n"
                f"Model Selection: {model_selection}\n"
                f"Task Parameters: {task_params}\n"
                "Provide assessment with success metrics, potential errors, and deployment recommendations."
            )
            response = await openai.ChatCompletion.acreate(
                model=model_selection,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            assessment = response.choices[0].message.content.strip()
            result = {
                "success": True,
                "metrics": {"assessment_detail": "Completed assessment."},
                "errors": None,
                "deployment_recommendations": assessment
            }
            logger.info(
                f"Assessment completed successfully for task: {task_description}")
        except Exception as e:
            logger.error(f"Error during assessment: {e}")
            result = {
                "success": False,
                "metrics": None,
                "errors": str(e),
                "deployment_recommendations": "N/A"
            }
        return result

    async def refine_task_outcome(self, task_id: str, proposal: str, feedback: str) -> str:
        """
        Refine a rejected task proposal based on feedback.
        - Records the rejection reason.
        - Chooses an alternate model based on the feedback.
        - Retries generating a revised proposal.
        """
        # Log and record feedback
        logger.info(f"[Feedback Pattern] Task {task_id} rejected: {feedback}")
        self.task_feedback_history.setdefault(task_id, []).append(feedback)

        # Determine alternate model based on feedback keywords
        lower_feedback = feedback.lower()
        if "syntax" in lower_feedback or "bug" in lower_feedback:
            new_model = "code-davinci-002"
        elif "slow" in lower_feedback or "performance" in lower_feedback:
            new_model = "gpt-3.5-turbo"
        else:
            new_model = "gpt-4"

        # Create a new prompt incorporating feedback for re-generation
        new_prompt = (
            f"Original Proposal: {proposal}\n"
            f"Feedback: {feedback}\n"
            "Please provide an improved version of the proposal addressing the feedback."
        )

        try:
            response = await openai.ChatCompletion.acreate(
                model=new_model,
                messages=[{"role": "user", "content": new_prompt}],
                max_tokens=150
            )
            revised_proposal = response.choices[0].message.content.strip()
            if not revised_proposal:
                raise ValueError("Revised proposal empty")
            logger.info(
                f"[Feedback Pattern] Revised proposal generated using model {new_model} for task {task_id}")
            return revised_proposal
        except Exception as e:
            logger.error(
                f"[Feedback Pattern] Retry failed for task {task_id}: {e}")
            return "Fallback: Please adjust the proposal manually based on the retrieved feedback."

    async def escalate_to_user(self, unresolved_issues: List[Dict[str, str]]) -> str:
        """
        Summarizes unresolved circular issues and provides prioritized actionable asks.

        Each issue in 'unresolved_issues' should be a dict with keys:
          - 'description': A brief description of the issue.
          - 'attempts': What Cherry tried autonomously.
          - 'fail_reason': Why those solutions failed.

        Returns:
            A conversational message with a summary of issues and prioritized asks.
        """
        # Summarize each unresolved issue
        summaries = []
        for issue in unresolved_issues:
            summaries.append(
                f"Issue: {issue.get('description', 'N/A')}\n"
                f"  Tried: {issue.get('attempts', 'N/A')}\n"
                f"  Failed Because: {issue.get('fail_reason', 'N/A')}"
            )
        issues_summary = "\n\n".join(summaries)

        # Create a prioritized list of actionable asks
        asks = [
            "Verify your project configurations and settings.",
            "Confirm that all required policies and permissions are correctly set.",
            "Ensure that necessary tools or APIs are unlocked (e.g., verify your payment status here: https://platform.openai.com/account/billing).",
            "Review any recent environment changes that might affect system functionality."
        ]
        prioritized_asks = "\n".join(
            [f"{idx+1}. {ask}" for idx, ask in enumerate(asks)])

        # Compose the final message with a friendly tone
        message = (
            "Hello, it looks like I've encountered some issues that I couldn't resolve on my own. Here's a summary of what I've tried:\n\n"
            f"{issues_summary}\n\n"
            "Based on these challenges, could you please consider the following actions?\n"
            f"{prioritized_asks}\n\n"
            "Your assistance is greatly appreciated!"
        )
        return message

    async def multi_layer_fallback(self, api_call, prompt: str, *args, alternative_model="code-davinci-002", retries=3, **kwargs):
        """
        Dynamically adjust Cherry’s approach when facing blocked or rate-limited responses.
        Steps:
         1. Attempt the API call with exponential backoff.
         2. If blocked, rephrase the prompt and retry.
         3. If still unsuccessful, switch to an alternative model.
         4. As a last resort, escalate the issue to the user.

        Integrates learning by recording fallback attempts.
        """
        # First attempt using exponential backoff handling
        try:
            result = await handle_rate_limits(api_call, *args, retries=retries, **kwargs)
            return result
        except Exception as e:
            error_message = str(e).lower()
            self.task_feedback_history.setdefault("multi_layer_fallback", []).append(
                f"Initial failure: {error_message}")

            # Check for rate-limit or blocked response signs
            if "rate limit" in error_message or "blocked" in error_message:
                # Attempt rephrasing the prompt
                try:
                    new_prompt = await self.dynamic_rephrase_prompt(prompt)
                    self.task_feedback_history["multi_layer_fallback"].append(
                        "Rephrased prompt")
                    result = await api_call(new_prompt, *args, **kwargs)
                    return result
                except Exception as e2:
                    self.task_feedback_history["multi_layer_fallback"].append(
                        f"Rephrase failure: {str(e2).lower()}")
                    # Retry using an alternative model if applicable
                    try:
                        alt_kwargs = kwargs.copy()
                        alt_kwargs["model"] = alternative_model
                        self.task_feedback_history["multi_layer_fallback"].append(
                            f"Switched to alternative model: {alternative_model}")
                        result = await api_call(prompt, *args, **alt_kwargs)
                        return result
                    except Exception as e3:
                        self.task_feedback_history["multi_layer_fallback"].append(
                            f"Alternative model failure: {str(e3).lower()}")
                        # Escalate to user with actionable next steps
                        fallback_message = await self.escalate_to_user(
                            [{"description": "API call failed after multiple fallback layers.",
                              "attempts": "Initial, rephrase, alternative model",
                              "fail_reason": f"{e3}"}]
                        )
                        return fallback_message
            else:
                raise e

    async def collaborate_on_task(self, task: dict, dependencies: dict = None) -> dict:
        """
        Collaborate with other agents on a task.

        Steps:
        1. If a dependency graph is provided, check for circular dependencies.
        2. Build a message with task details and offload via message_bus.
        3. Log outcome and update agent score based on simulated feedback.
        """
        if dependencies:
            if dependency_checker(dependencies):
                return {"error": "Circular dependency detected."}
        message = {
            "sender": self.name,
            "recipient": task.get("assigned_agent", "unknown"),
            "type": "task_offload",
            "payload": task
        }
        response = await message_bus(message)
        # Simulated score update: successful delivery increases score.
        if response.get("status") == "delivered":
            update_agent_score(self.name, 1.0)
        return response

# New function to handle API rate-limit errors


async def handle_rate_limits(api_call, *args, retries=5, api_name="default", **kwargs):
    """
    Manages API rate-limit responses using exponential backoff with jitter.

    Args:
        api_call (coroutine): The API call to execute.
        *args: Positional arguments for the API call.
        api_name (str): Identifier for the API (useful for multi-rate-limit handling).
        retries (int): Maximum number of retry attempts.
        **kwargs: Keyword arguments for the API call.

    Returns:
        Result of the API call if successful.

    Raises:
        Exception if the rate limit persists after the max retries.
    """
    base_delay = 1  # Base delay in seconds
    for attempt in range(retries):
        try:
            return await api_call(*args, **kwargs)
        except Exception as e:
            # Detect rate-limit error via HTTP status attribute or error message content
            if (hasattr(e, "http_status") and e.http_status == 429) or "rate limit" in str(e).lower():
                # Calculate exponential backoff delay with jitter
                delay = base_delay * (2 ** attempt) + \
                    random.uniform(0, base_delay)
                logger.warning(
                    f"API '{api_name}' rate limit encountered: {e}. Retrying in {delay:.2f} seconds (attempt {attempt+1}/{retries}).")
                await asyncio.sleep(delay)
                continue
            else:
                raise e
    logger.error(
        f"Exceeded max retries ({retries}) for API '{api_name}' due to rate limits.")
    raise Exception(
        f"Rate limit exceeded for API '{api_name}' after {retries} attempts.")
