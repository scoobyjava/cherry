# orchestrator.py (Fixed imports, ready-to-run)
import asyncio
import networkx as nx
from typing import Dict, Any, List
from dataclasses import dataclass, field
from config import Config
from logger import logger
from memory_chroma import ChromaMemory
from agent_factory import AgentFactory  # Corrected import!

@dataclass
class TaskDependency:
    prerequisite_ids: List[int] = field(default_factory=list)

@dataclass
class TaskMetrics:
    attempts: int = 0
    success_rate: float = 0.0
    avg_processing_time: float = 0.0

class AdvancedOrchestrator:
    def __init__(self):
        self.tasks = asyncio.PriorityQueue()
        self.completed_tasks = {}
        self.task_metrics: Dict[int, TaskMetrics] = {}
        self.dependency_graph = nx.DiGraph()
        self.memory = ChromaMemory(collection_name="cherry_primary_memory")
        self.agent_factory = AgentFactory()  # Load dynamically created agents correctly
        self.agents = {agent_name: agent_class() for agent_name, agent_class in self.agent_factory.agents.items()}
        self.running = False

    async def add_task(self, description: str, priority: int = 1, dependencies: TaskDependency = None) -> int:
        task_id = int(asyncio.get_event_loop().time() * 1000)
        task = {"id": task_id, "description": description, "priority": priority, "dependencies": dependencies or TaskDependency()}
        await self.tasks.put((priority, task))
        self.dependency_graph.add_node(task_id)
        for dep_id in task["dependencies"].prerequisite_ids:
            self.dependency_graph.add_edge(dep_id, task_id)
        return task_id

    async def process_task(self, task: Dict[str, Any]):
        agent = self.determine_agent(task["description"])
        if not agent:
            logger.warning(f"No suitable agent found for task {task['id']}")
            return

        try:
            result = await agent.process(task)
            self.memory.insert_text(task["description"], result, doc_id=str(task["id"]))
            self.completed_tasks[task["id"]] = result
            logger.info(f"Task {task['id']} processed successfully by {agent.name}.")
        except Exception as e:
            logger.error(f"Error processing task {task['id']} with {agent.name}: {e}")

    def determine_agent(self, description: str):
        for agent in self.agents.values():
            if agent.can_handle(description):
                return agent
        return None

    async def run(self):
        self.running = True
        logger.info("🍒 AdvancedOrchestrator running...")
        while self.running:
            if not self.tasks.empty():
                priority, task = await self.tasks.get()
                await self.process_task(task)
            await asyncio.sleep(0.1)

    def stop(self):
        self.running = False
        logger.info("AdvancedOrchestrator stopped.")

if __name__ == "__main__":
    orchestrator = AdvancedOrchestrator()
    asyncio.run(orchestrator.run())
# Intentionally inefficient test function for CodeRabbit
def redundant_function():
    for i in range(0, 5):
        print(i)
        for j in range(0, 5):
            print(j)
