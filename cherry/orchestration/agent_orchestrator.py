import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from cherry.agents.base_agent import Agent
from cherry.memory.agent_memory import share_memory_between_agents, retrieve_shared_memories

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Orchestrates multiple agents, routing tasks to the most appropriate agent
    and managing workflows that involve collaboration between agents.
    """
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.workflows: Dict[str, List[str]] = {}
        self._task_queue = asyncio.Queue()
        self._results_cache: Dict[str, Any] = {}
    
    def register_agent(self, agent: Agent) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent: The agent instance to register
        """
        self.agents[agent.name] = agent
        logger.info(f"Agent registered: {agent.name}")
    
    def register_workflow(self, workflow_name: str, agent_sequence: List[str]) -> None:
        """
        Register a workflow consisting of a sequence of agents.
        
        Args:
            workflow_name: Unique name for the workflow
            agent_sequence: Ordered list of agent names that form the workflow
        """
        # Validate all agents exist
        missing_agents = [name for name in agent_sequence if name not in self.agents]
        if missing_agents:
            raise ValueError(f"Cannot create workflow: agents not registered: {missing_agents}")
        
        self.workflows[workflow_name] = agent_sequence
        logger.info(f"Workflow registered: {workflow_name} with agents {agent_sequence}")
    
    def find_suitable_agents(self, task_description: str) -> List[str]:
        """
        Find agents that can handle a specific task based on their capabilities.
        
        Args:
            task_description: Description of the task to be performed
            
        Returns:
            List of agent names that can handle the task
        """
        suitable_agents = [
            name for name, agent in self.agents.items() 
            if agent.can_handle(task_description)
        ]
        
        if not suitable_agents:
            logger.warning(f"No suitable agents found for task: {task_description}")
        
        return suitable_agents
    
    async def execute_task(self, task_data: Dict[str, Any], agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a task using a specific agent or find a suitable one.
        
        Args:
            task_data: The data required for the task
            agent_name: Optional name of the agent to use
            
        Returns:
            The result of the task execution
        """
        if agent_name:
            if agent_name not in self.agents:
                raise ValueError(f"Agent not found: {agent_name}")
            agent = self.agents[agent_name]
        else:
            # Find suitable agent based on task description
            suitable_agents = self.find_suitable_agents(task_data.get('description', ''))
            if not suitable_agents:
                raise ValueError("No suitable agent found for this task")
            agent = self.agents[suitable_agents[0]]  # Use the first suitable agent
        
        logger.info(f"Executing task with agent: {agent.name}")
        result = await agent.process(task_data)
        
        # Cache the result for potential use by other agents
        task_id = task_data.get('id', str(id(task_data)))
        self._results_cache[task_id] = result
        
        return result
    
    async def execute_workflow(self, workflow_name: str, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a predefined workflow of sequential agent tasks.
        
        Args:
            workflow_name: Name of the workflow to execute
            initial_data: Initial data to provide to the first agent
            
        Returns:
            The result of the final agent in the workflow
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_name}")
        
        agent_sequence = self.workflows[workflow_name]
        current_data = initial_data
        results = {}
        
        for i, agent_name in enumerate(agent_sequence):
            logger.info(f"Workflow {workflow_name}: Step {i+1}/{len(agent_sequence)} using {agent_name}")
            
            # Share memory with next agent if this isn't the first agent
            if i > 0:
                previous_agent = agent_sequence[i-1]
                memory_id = share_memory_between_agents(
                    previous_agent,
                    agent_name,
                    f"Workflow step data: {current_data}"
                )
                logger.info(f"Shared memory {memory_id} from {previous_agent} to {agent_name}")
            
            # Execute this step in the workflow
            step_result = await self.execute_task(current_data, agent_name)
            results[agent_name] = step_result
            current_data = {**current_data, **step_result}  # Merge results with current data
        
        return {
            "workflow": workflow_name,
            "final_result": current_data,
            "step_results": results
        }
    
    async def collaborative_task(self, task_data: Dict[str, Any], agent_names: List[str]) -> Dict[str, Any]:
        """
        Execute a task collaboratively using multiple agents in parallel.
        
        Args:
            task_data: The data required for the task
            agent_names: Names of agents to collaborate on this task
            
        Returns:
            Combined results from all agents
        """
        if not agent_names:
            raise ValueError("No agents specified for collaborative task")
        
        missing_agents = [name for name in agent_names if name not in self.agents]
        if missing_agents:
            raise ValueError(f"Agents not registered: {missing_agents}")
        
        # Execute tasks in parallel
        tasks = [self.execute_task(task_data, agent_name) for agent_name in agent_names]
        results = await asyncio.gather(*tasks)
        
        # Share results between agents
        for i, source_agent in enumerate(agent_names):
            for target_agent in agent_names:
                if source_agent != target_agent:
                    share_memory_between_agents(
                        source_agent,
                        target_agent,
                        f"Collaborative result: {results[i]}"
                    )
        
        # Combine results
        combined_result = {}
        for i, result in enumerate(results):
            combined_result[agent_names[i]] = result
            
        return {
            "collaborative_task": True,
            "agents": agent_names,
            "results": combined_result
        }
    
    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """Get an agent by name"""
        return self.agents.get(agent_name)
    
    def list_agents(self) -> List[str]:
        """List all registered agents"""
        return list(self.agents.keys())
    
    def list_workflows(self) -> List[str]:
        """List all registered workflows"""
        return list(self.workflows.keys())