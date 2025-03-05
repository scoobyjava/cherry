import os
import logging
import asyncio
import inspect
import json
import time
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import importlib.util
import numpy as np
from collections import defaultdict

from cherry.agents.base_agent import Agent
from cherry.feedback.system_evaluator import get_evaluator
from cherry.orchestration.scheduler import initialize_monitoring

logger = logging.getLogger(__name__)

@dataclass
class AgentRequirement:
    """Specification for a needed agent capability"""
    name: str
    purpose: str
    problem_solved: str
    capabilities: List[str]
    interfaces: List[str]
    priority: float  # 0.0 to 1.0
    failure_patterns: List[Dict[str, Any]]
    bottleneck_data: Dict[str, Any]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {k: v for k, v in self.__dict__.items()}
        result["created_at"] = self.created_at.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentRequirement':
        """Create from dictionary representation"""
        if isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class AgentBlueprint:
    """Blueprint for a new agent implementation"""
    requirement: AgentRequirement
    class_name: str
    code: str
    test_cases: List[Dict[str, Any]]
    dependencies: List[str]
    integration_points: Dict[str, str]
    created_at: datetime = None
    created_by: str = "co-pilot"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {k: v for k, v in self.__dict__.items()}
        result["requirement"] = self.requirement.to_dict()
        result["created_at"] = self.created_at.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentBlueprint':
        """Create from dictionary representation"""
        data["requirement"] = AgentRequirement.from_dict(data["requirement"])
        if isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


class AgentEvaluationMetrics:
    """Metrics collected during agent evaluation phase"""
    
    def __init__(self):
        self.task_success_rate = 0.0
        self.avg_response_time = 0.0
        self.memory_usage = 0.0
        self.error_count = 0
        self.collaboration_score = 0.0
        self.task_executions = []
        self.integration_success = False
        self.test_results = {}
        self.start_time = datetime.now()
        self.evaluation_duration = 0
        
    def calculate_final_score(self) -> float:
        """Calculate weighted score from all metrics (0.0 to 1.0)"""
        weights = {
            "task_success_rate": 0.4,
            "avg_response_time_score": 0.2,  # Converted to score 
            "memory_usage_score": 0.1,       # Converted to score
            "error_rate": 0.15,              # Inverse of error count
            "collaboration_score": 0.15
        }
        
        # Convert response time to score (lower is better)
        response_time_score = max(0.0, 1.0 - (self.avg_response_time / 5.0))
        
        # Convert memory usage to score (lower is better)
        memory_score = max(0.0, 1.0 - (self.memory_usage / 500.0))
        
        # Convert error count to rate (lower is better)
        error_rate = 0.0 if not self.task_executions else 1.0 - (self.error_count / max(1, len(self.task_executions)))
        
        scores = {
            "task_success_rate": self.task_success_rate,
            "avg_response_time_score": response_time_score,
            "memory_usage_score": memory_score,
            "error_rate": error_rate,
            "collaboration_score": self.collaboration_score
        }
        
        # Apply weights
        final_score = sum(weight * scores[key] for key, weight in weights.items())
        return final_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {k: v for k, v in self.__dict__.items() if k != 'task_executions'}
        result["task_execution_count"] = len(self.task_executions)
        result["start_time"] = self.start_time.isoformat()
        result["final_score"] = self.calculate_final_score()
        return result


class AgentFactory:
    """System for dynamically generating, deploying and evaluating new agents"""
    
    def __init__(self, agent_directory: str = None):
        self.agent_directory = agent_directory or os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents")
        self.sandbox_directory = os.path.join(self.agent_directory, "sandbox")
        self.requirements_directory = os.path.join(os.path.dirname(__file__), "requirements")
        self.blueprints_directory = os.path.join(os.path.dirname(__file__), "blueprints")
        self.evaluations_directory = os.path.join(os.path.dirname(__file__), "evaluations")
        
        # Ensure directories exist
        os.makedirs(self.sandbox_directory, exist_ok=True)
        os.makedirs(self.requirements_directory, exist_ok=True)
        os.makedirs(self.blueprints_directory, exist_ok=True)
        os.makedirs(self.evaluations_directory, exist_ok=True)
        
        # Track active evaluations
        self.active_evaluations = {}
        
        # Integrate with monitoring
        self.tracer = initialize_monitoring()
        
    async def analyze_system_for_requirements(self, threshold: float = 0.7) -> List[AgentRequirement]:
        """
        Analyze system performance and identify needs for new agents
        
        Args:
            threshold: Minimum severity threshold (0.0-1.0) for generating requirements
            
        Returns:
            List of agent requirements identified from system performance data
        """
        evaluator = get_evaluator()
        evaluation = await evaluator.run_system_evaluation()
        
        requirements = []
        
        # Look for bottlenecks that suggest new agent types
        for bottleneck in evaluation.get("bottlenecks", []):
            # Skip low severity bottlenecks
            severity_map = {"critical": 0.9, "high": 0.7, "medium": 0.5, "low": 0.3}
            severity_score = severity_map.get(bottleneck.get("severity", "low"), 0.3)
            if severity_score < threshold:
                continue
                
            # Analyze bottleneck to determine required capabilities
            bottleneck_type = bottleneck.get("bottleneck_type", "")
            if bottleneck_type == "communication_sink":
                # Too many messages coming to one agent - need a router/balancer
                requirements.append(
                    AgentRequirement(
                        name=f"load_balancer_{bottleneck.get('agent', 'unknown')}",
                        purpose="Distribute workload from overloaded agent",
                        problem_solved=f"Reduce message congestion at {bottleneck.get('agent')}",
                        capabilities=["load_balancing", "message_routing", "priority_queuing"],
                        interfaces=["message_bus"],
                        priority=severity_score,
                        failure_patterns=[],
                        bottleneck_data=bottleneck
                    )
                )
            elif bottleneck_type == "high_failure_rate":
                # Agent is failing too often - need a specialist or fallback
                requirements.append(
                    AgentRequirement(
                        name=f"specialist_{bottleneck.get('agent', 'unknown').lower()}",
                        purpose=f"Provide specialized handling for {bottleneck.get('agent')} failures",
                        problem_solved=f"Reduce failure rate of {bottleneck.get('agent')}",
                        capabilities=["error_handling", "specialized_processing"],
                        interfaces=["agent_api", "message_bus"],
                        priority=severity_score,
                        failure_patterns=[],
                        bottleneck_data=bottleneck
                    )
                )
            elif bottleneck_type == "slow_response":
                # Agent is too slow - need a performance optimizer
                requirements.append(
                    AgentRequirement(
                        name=f"accelerator_{bottleneck.get('agent', 'unknown').lower()}",
                        purpose=f"Optimize performance for {bottleneck.get('agent')}",
                        problem_solved=f"Improve response time of {bottleneck.get('agent')}",
                        capabilities=["parallel_processing", "caching", "request_optimization"],
                        interfaces=["agent_api"],
                        priority=severity_score,
                        failure_patterns=[],
                        bottleneck_data=bottleneck
                    )
                )
        
        # Process agent suggestions from the evaluation
        for suggestion in evaluation.get("suggested_agents", []):
            priority = 0.8 if suggestion.get("priority") == "high" else 0.5
            
            if "agent_role" in suggestion:
                # Direct agent role suggestion
                requirements.append(
                    AgentRequirement(
                        name=f"{suggestion['agent_role']}",
                        purpose=suggestion.get("rationale", "Improve system performance"),
                        problem_solved=suggestion.get("rationale", "Address system need"),
                        capabilities=[suggestion['agent_role']],
                        interfaces=["message_bus"],
                        priority=priority,
                        failure_patterns=[],
                        bottleneck_data={}
                    )
                )
            elif "task_specialization" in suggestion:
                # Task specialization suggestion
                requirements.append(
                    AgentRequirement(
                        name=f"{suggestion['task_specialization']}_specialist",
                        purpose=f"Handle {suggestion['task_specialization']} tasks",
                        problem_solved=suggestion.get("rationale", f"Provide specialized {suggestion['task_specialization']} processing"),
                        capabilities=[suggestion['task_specialization'], "specialized_processing"],
                        interfaces=["message_bus"],
                        priority=priority,
                        failure_patterns=[],
                        bottleneck_data={}
                    )
                )
        
        # Save unique requirements
        saved_names = set()
        for req in requirements:
            if req.name not in saved_names:
                self._save_requirement(req)
                saved_names.add(req.name)
        
        return requirements
    
    def _save_requirement(self, requirement: AgentRequirement) -> None:
        """Save agent requirement to file"""
        filename = f"{requirement.name}_{int(time.time())}.json"
        filepath = os.path.join(self.requirements_directory, filename)
        
        with open(filepath, 'w') as f:
            json.dump(requirement.to_dict(), f, indent=2)
            
        logger.info(f"Saved agent requirement: {filepath}")
    
    async def generate_agent_blueprint(self, requirement: AgentRequirement) -> AgentBlueprint:
        """
        Generate an agent blueprint from a requirement
        
        This is where Co-Pilot would evaluate the requirement and propose an agent implementation.
        In a real system, this might call an external API or AI service.
        """
        logger.info(f"Requesting agent blueprint for {requirement.name}")
        
        # This is a simplified version - in reality this would call Co-Pilot
        # to generate the actual agent implementation code
        
        # Generate a class name from the requirement name
        class_name = "".join(word.capitalize() for word in requirement.name.split('_')) + "Agent"
        
        # Generate stub code for the new agent
        code = self._generate_agent_code_template(class_name, requirement)
        
        # Generate test cases for the new agent
        test_cases = self._generate_test_cases(requirement)
        
        # Identify integration points based on interfaces
        integration_points = {}
        if "message_bus" in requirement.interfaces:
            integration_points["message_bus"] = "register_with_message_bus"
        if "agent_api" in requirement.interfaces:
            integration_points["agent_api"] = "register_with_agent_manager"
        
        blueprint = AgentBlueprint(
            requirement=requirement,
            class_name=class_name,
            code=code,
            test_cases=test_cases,
            dependencies=["base_agent"],
            integration_points=integration_points,
            created_by="auto-generator" # Would be "co-pilot" in the real system
        )
        
        # Save the blueprint
        self._save_blueprint(blueprint)
        
        return blueprint
    
    def _generate_agent_code_template(self, class_name: str, requirement: AgentRequirement) -> str:
        """Generate template code for a new agent"""
        # This is a simplified template - a real system would generate more complete code
        code_template = f"""
import logging
import asyncio
from typing import Dict, Any, List, Optional
from cherry.agents.base_agent import Agent

logger = logging.getLogger(__name__)

class {class_name}(Agent):
    \"\"\"
    {requirement.purpose}
    
    Solves: {requirement.problem_solved}
    \"\"\"
    
    def __init__(self, name: str = "{requirement.name}", description: str = "{requirement.purpose}"):
        super().__init__(name, description)
        self.capabilities = {requirement.capabilities}
        
    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Process tasks according to this agent's specialization
        \"\"\"
        logger.info(f"Processing task with {{self.name}}")
        
        # Implementation would be filled in here
        
        result = {{
            "status": "success",
            "message": f"{{self.name}} processed task",
            "data": {{}}
        }}
        
        return result
        
    async def _handle_specialized_task(self, task_details: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Handle specialized processing for this agent's domain\"\"\"
        # Implementation would go here
        pass
"""
        return code_template
    
    def _generate_test_cases(self, requirement: AgentRequirement) -> List[Dict[str, Any]]:
        """Generate test cases for the new agent"""
        # A real system would generate more comprehensive tests
        test_cases = [
            {
                "name": "basic_functionality",
                "input": {"task_type": "basic", "data": {"test": "value"}},
                "expected_output_contains": ["success"]
            },
            {
                "name": "error_handling",
                "input": {"task_type": "error_test", "data": {"cause_error": True}},
                "expected_output_contains": ["error", "handled"]
            }
        ]
        
        # Add capability-specific tests
        for capability in requirement.capabilities:
            test_cases.append({
                "name": f"{capability}_test",
                "input": {"task_type": capability, "data": {"capability_test": True}},
                "expected_output_contains": ["success", capability]
            })
            
        return test_cases
    
    def _save_blueprint(self, blueprint: AgentBlueprint) -> None:
        """Save agent blueprint to file"""
        filename = f"{blueprint.requirement.name}_{int(time.time())}.json"
        filepath = os.path.join(self.blueprints_directory, filename)
        
        with open(filepath, 'w') as f:
            json.dump(blueprint.to_dict(), f, indent=2)
            
        logger.info(f"Saved agent blueprint: {filepath}")
    
    async def deploy_agent_to_sandbox(self, blueprint: AgentBlueprint) -> str:
        """
        Deploy agent to sandbox environment for evaluation
        
        Returns:
            Path to the deployed agent module
        """
        logger.info(f"Deploying agent {blueprint.class_name} to sandbox")
        
        # Create a unique filename for the agent
        timestamp = int(time.time())
        module_name = f"sandbox_{blueprint.requirement.name}_{timestamp}"
        filename = f"{module_name}.py"
        filepath = os.path.join(self.sandbox_directory, filename)
        
        # Write the agent code to file
        with open(filepath, 'w') as f:
            f.write(blueprint.code)
        
        logger.info(f"Agent deployed to sandbox: {filepath}")
        return filepath
    
    async def evaluate_agent(self, agent_path: str, blueprint: AgentBlueprint) -> AgentEvaluationMetrics:
        """
        Evaluate an agent's performance against test cases and live tasks
        
        Args:
            agent_path: Path to the deployed agent module
            blueprint: The blueprint that describes the agent
            
        Returns:
            Evaluation metrics for the agent
        """
        logger.info(f"Beginning evaluation of agent: {agent_path}")
        
        # Initialize metrics
        metrics = AgentEvaluationMetrics()
        
        try:
            # Load the agent module
            module_name = os.path.basename(agent_path).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, agent_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the agent class
            agent_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Agent) and obj.__name__ == blueprint.class_name:
                    agent_class = obj
                    break
            
            if not agent_class:
                logger.error(f"Could not find agent class {blueprint.class_name} in {agent_path}")
                metrics.error_count += 1
                return metrics
            
            # Instantiate the agent
            agent = agent_class()
            
            # Run test cases
            passed_tests = 0
            for test_case in blueprint.test_cases:
                try:
                    # Track execution time
                    start_time = time.time()
                    result = await agent.process(test_case["input"])
                    execution_time = time.time() - start_time
                    
                    # Check if result contains expected strings
                    test_passed = all(
                        expected in str(result) 
                        for expected in test_case["expected_output_contains"]
                    )
                    
                    if test_passed:
                        passed_tests += 1
                    
                    # Record test execution
                    metrics.task_executions.append({
                        "test_name": test_case["name"],
                        "success": test_passed,
                        "execution_time": execution_time,
                        "input": test_case["input"],
                        "output": result
                    })
                    
                    # Update response time metric
                    if metrics.avg_response_time == 0:
                        metrics.avg_response_time = execution_time
                    else:
                        metrics.avg_response_time = (metrics.avg_response_time + execution_time) / 2
                    
                except Exception as e:
                    logger.error(f"Error in test case {test_case['name']}: {str(e)}")
                    metrics.error_count += 1
                    metrics.task_executions.append({
                        "test_name": test_case["name"],
                        "success": False,
                        "error": str(e),
                        "input": test_case["input"]
                    })
            
            # Calculate success rate
            metrics.task_success_rate = passed_tests / len(blueprint.test_cases)
            
            # Execute integration tests - check that the agent can integrate with the system
            try:
                # Example: Check if the agent can register with the message bus
                if "message_bus" in blueprint.integration_points:
                    # Simulate integration - in a real system we would actually test this
                    metrics.integration_success = True
                
                # Set a baseline collaboration score - would be measured in real system
                metrics.collaboration_score = 0.5 
            except Exception as e:
                logger.error(f"Integration test failed: {str(e)}")
                metrics.integration_success = False
            
            # Record overall evaluation duration
            metrics.evaluation_duration = (datetime.now() - metrics.start_time).total_seconds()
            
            # Save evaluation results
            self._save_evaluation_results(blueprint.requirement.name, metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Agent evaluation failed: {str(e)}")
            metrics.error_count += 1
            return metrics
    
    def _save_evaluation_results(self, agent_name: str, metrics: AgentEvaluationMetrics) -> None:
        """Save agent evaluation results to file"""
        filename = f"{agent_name}_eval_{int(time.time())}.json"
        filepath = os.path.join(self.evaluations_directory, filename)
        
        with open(filepath, 'w') as f:
            json.dump(metrics.to_dict(), f, indent=2)
            
        logger.info(f"Saved agent evaluation: {filepath}")
    
    async def promote_agent_to_production(self, agent_path: str, blueprint: AgentBlueprint) -> bool:
        """
        Promote an agent from sandbox to production if it passes evaluation
        
        Args:
            agent_path: Path to the agent in sandbox
            blueprint: The blueprint for the agent
            
        Returns:
            True if promotion was successful
        """
        # Determine destination path
        module_name = blueprint.requirement.name
        module_path = os.path.join(self.agent_directory, f"{module_name}_agent.py")
        
        logger.info(f"Promoting agent from {agent_path} to {module_path}")
        
        # Read the agent code
        with open(agent_path, 'r') as f:
            code = f.read()
        
        # Write to production location
        with open(module_path, 'w') as f:
            f.write(code)
        
        # Now the agent can be imported by the system
        logger.info(f"Successfully promoted agent to production: {module_path}")
        return True
            
    async def agent_evolution_cycle(self, evaluation_threshold: float = 0.7) -> None:
        """
        Run a complete agent evolution cycle:
        1. Analyze system for needs
        2. Generate blueprints for required agents
        3. Deploy to sandbox
        4. Evaluate performance
        5. Promote successful agents
        """
        try:
            # Step 1: Analyze system and identify requirements
            requirements = await self.analyze_system_for_requirements()
            if not requirements:
                logger.info("No new agent requirements identified")
                return
            
            for requirement in requirements:
                try:
                    # Step 2: Generate blueprint
                    blueprint = await self.generate_agent_blueprint(requirement)
                    
                    # Step 3: Deploy to sandbox
                    sandbox_path = await self.deploy_agent_to_sandbox(blueprint)
                    
                    # Step 4: Evaluate
                    metrics = await self.evaluate_agent(sandbox_path, blueprint)
                    final_score = metrics.calculate_final_score()
                    
                    logger.info(f"Agent {requirement.name} evaluation score: {final_score:.2f}")
                    
                    # Step 5: Promote if successful
                    if final_score >= evaluation_threshold:
                        success = await self.promote_agent_to_production(sandbox_path, blueprint)
                        if success:
                            logger.info(f"Agent {requirement.name} successfully promoted to production")
                        else:
                            logger.warning(f"Failed to promote agent {requirement.name} to production")
                    else:
                        logger.info(f"Agent {requirement.name} did not meet promotion threshold ({final_score:.2f} < {evaluation_threshold:.2f})")
                        
                except Exception as e:
                    logger.error(f"Error in agent evolution cycle for {requirement.name}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error in agent evolution cycle: {str(e)}")


# Initialize the agent factory
agent_factory = AgentFactory()

# Schedule the agent evolution cycle to run periodically
async def run_agent_evolution_cycle():
    """Run the agent evolution cycle periodically"""
    while True:
        await agent_factory.agent_evolution_cycle()
        # Run once per day
        await asyncio.sleep(86400)


class AgentRequestHandler:
    """
    Handles explicit requests for new agent creation from other parts of the system
    """
    def __init__(self):
        self.factory = agent_factory
    
    async def request_new_agent(self, 
                              name: str,
                              purpose: str, 
                              problem_description: str,
                              capabilities: List[str],
                              priority: float = 0.5) -> str:
        """
        Request creation of a new agent type
        
        Args:
            name: Suggested name for the agent
            purpose: What the agent should do
            problem_description: What problem it solves
            capabilities: List of capabilities the agent should have
            priority: Priority of this request (0.0-1.0)
            
        Returns:
            ID of the request for tracking
        """
        # Create a requirement
        requirement = AgentRequirement(
            name=name,
            purpose=purpose,
            problem_solved=problem_description,
            capabilities=capabilities,
            interfaces=["message_bus"],
            priority=priority,
            failure_patterns=[],
            bottleneck_data={}
        )
        
        # Save the requirement
        self._save_requirement(requirement)
        
        # Trigger the agent creation process
        asyncio.create_task(self._process_agent_request(requirement))
        
        # Return an ID for tracking
        return f"{name}_{int(time.time())}"
    
    def _save_requirement(self, requirement):
        """Save the requirement to the factory's storage"""
        self.factory._save_requirement(requirement)
    
    async def _process_agent_request(self, requirement):
        """Process a request for a new agent"""
        try:
            # Generate blueprint
            blueprint = await self.factory.generate_agent_blueprint(requirement)
            
            # Deploy to sandbox
            sandbox_path = await self.factory.deploy_agent_to_sandbox(blueprint)
            
            # Evaluate
            metrics = await self.factory.evaluate_agent(sandbox_path, blueprint)
            
            # Promote if score is above threshold
            if metrics.calculate_final_score() >= 0.7:
                await self.factory.promote_agent_to_production(sandbox_path, blueprint)
                
        except Exception as e:
            logger.error(f"Error processing agent request {requirement.name}: {str(e)}")


# Create singleton request handler
agent_request_handler = AgentRequestHandler()