import asyncio
import time
import json
import networkx as nx
from threading import Lock
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

import openai
from config import Config
from logger import logger
from memory_chroma import ChromaMemory

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain_community.utilities.google_search import GoogleSearchAPIWrapper
from langchain_experimental.tools.python.tool import PythonREPLTool

@dataclass
class TaskDependency:
    prerequisite_ids: List[int] = field(default_factory=list)
    blocking_conditions: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class TaskMetrics:
    attempts: int = 0
    success_rate: float = 0.0
    avg_processing_time: float = 0.0
    last_execution_time: float = 0.0
    total_processing_time: float = 0.0

class TaskOrchestrationError(Exception):
    pass

class AdvancedOrchestrator:
    def __init__(self, config_path: str = 'config.json'):
        self.task_queue = []
        self.completed_tasks = []
        self.task_dependency_graph = nx.DiGraph()
        self.task_metrics: Dict[int, TaskMetrics] = {}
        self.lock = Lock()
        self.running = False
        self.agent_performance: Dict[str, Dict[str, Any]] = {}

        self.load_configuration(config_path)
        self._init_memory_system()
        self._init_llm_clients()
        self._init_tools()
        self._init_agents()
        
        self.loop = asyncio.new_event_loop()

    def load_configuration(self, config_path: str):
        try:
            with open(config_path, 'r') as config_file:
                self.advanced_config = json.load(config_file)
        except FileNotFoundError:
            logger.warning(f"{config_path} not found, loading defaults.")
            self.advanced_config = {
                "max_concurrent_tasks": 5,
                "task_timeout": 3600,
                "agent_performance_threshold": 0.7
            }

    def _init_memory_system(self):
        try:
            self.primary_memory = ChromaMemory(collection_name="cherry_primary_memory")
            self.task_memory = ChromaMemory(collection_name="cherry_task_memory")
            self.agent_memory = ChromaMemory(collection_name="cherry_agent_memory")
            logger.info("Memory system initialized.")
        except Exception as e:
            logger.error(f"Memory init failed: {e}")
            self.primary_memory = None

    def _init_llm_clients(self):
        self.api_key = Config.OPENAI_API_KEY
        self.langchain_llms = {
            "creative": ChatOpenAI(api_key=self.api_key, model="gpt-4-turbo", temperature=0.8),
            "analytical": ChatOpenAI(api_key=self.api_key, model="gpt-3.5-turbo", temperature=0.3)
        }

    def _init_tools(self):
        self.tool_registry = {}
        standard_tools = [PythonREPLTool(), GoogleSearchAPIWrapper()]
        for tool in standard_tools:
            wrapped_tool = Tool(name=type(tool).__name__, func=tool.run, description=f"{type(tool).__name__} tool")
            self.tool_registry[wrapped_tool.name] = wrapped_tool
            logger.info(f"Tool initialized: {wrapped_tool.name}")

    def _init_agents(self):
        self.agents = {}
        agent_configs = [
            {"name": "research_agent", "prompt": "You are a research expert.", "llm": self.langchain_llms["analytical"]},
            {"name": "creative_agent", "prompt": "You are a creative innovator.", "llm": self.langchain_llms["creative"]}
        ]
        for config in agent_configs:
            agent_prompt = ChatPromptTemplate.from_template(config["prompt"])
            agent = create_react_agent(config["llm"], list(self.tool_registry.values()), agent_prompt)
            executor = AgentExecutor(agent=agent, tools=list(self.tool_registry.values()), verbose=True, handle_parsing_errors=True)
            self.agents[config["name"]] = executor
            logger.info(f"Agent initialized: {config['name']}")

    def add_task(self, description: str, priority: int = 1, context: Dict[str, Any] = None, dependencies: TaskDependency = None) -> int:
        task_id = int(time.time() * 1000)
        task = {
            "id": task_id,
            "description": description,
            "priority": priority,
            "status": "pending",
            "context": context or {},
            "created_at": time.time(),
            "dependencies": dependencies or TaskDependency()
        }
        with self.lock:
            self.task_queue.append(task)
            self.task_queue.sort(key=lambda x: x["priority"], reverse=True)
        self.task_dependency_graph.add_node(task_id)
        for dep_id in task["dependencies"].prerequisite_ids:
            self.task_dependency_graph.add_edge(dep_id, task_id)
        self.task_metrics[task_id] = TaskMetrics()

        try:
            embedding = self.get_embedding(description)
            self.primary_memory.insert_text(description, embedding, doc_id=str(task_id))
        except Exception as e:
            logger.error(f"Embedding storage failed for task {task_id}: {e}")
        return task_id

    def get_embedding(self, text: str) -> list:
        openai.api_key = self.api_key
        response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
        return response['data'][0]['embedding']

    def get_task_status(self, task_id: int) -> Dict[str, Any]:
        task = next((t for t in self.task_queue + self.completed_tasks if t["id"] == task_id), None)
        if task:
            return task
        return {"error": "Task not found"}

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        return self.task_queue + self.completed_tasks

    def clear_completed_tasks(self):
        with self.lock:
            self.completed_tasks.clear()

    def _process_task_with_llm(self, task: Dict[str, Any]) -> Dict[str, Any]:
        llm = self.langchain_llms["analytical"]
        response = llm.invoke(task["description"])
        return {"output": response.content}

    def determine_agent_type(self, description: str) -> str:
        if "research" in description.lower():
            return "research_agent"
        elif "creative" in description.lower():
            return "creative_agent"
        return "research_agent"

    def process_with_agent(self, task: Dict[str, Any]):
        result = self.process_task(task)
        task["result"] = result
        task["status"] = result["status"]

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        agent_type = self.determine_agent_type(task["description"])
        start_time = time.time()
        agent = self.agents[agent_type]
        result = agent.invoke({"task": task["description"]})
        metrics = self.task_metrics[task["id"]]
        metrics.attempts += 1
        metrics.success_rate = (metrics.success_rate * (metrics.attempts - 1) + 1) / metrics.attempts
        metrics.last_execution_time = time.time() - start_time
        metrics.total_processing_time += metrics.last_execution_time
        metrics.avg_processing_time = metrics.total_processing_time / metrics.attempts
        return {"status": "completed", "output": result, "agent": agent_type}

    def run(self):
        self.running = True
        logger.info("AdvancedOrchestrator started")
        while self.running:
            executable_tasks = [task for task in self.task_queue if self.can_execute_task(task)]
            for task in executable_tasks:
                self.process_with_agent(task)
                with self.lock:
                    self.task_queue.remove(task)
                    self.completed_tasks.append(task)
            time.sleep(0.1)

    def can_execute_task(self, task: Dict[str, Any]) -> bool:
        return all(prereq in [t["id"] for t in self.completed_tasks] for prereq in task["dependencies"].prerequisite_ids)

    def stop(self):
        self.running = False
        logger.info("AdvancedOrchestrator stopped")
    def checkpoint_state(self):
        state = {
            "task_queue": self.task_queue,
            "completed_tasks": self.completed_tasks,
            "task_metrics": {k: vars(v) for k, v in self.task_metrics.items()},
        }
        try:
            with open("cherry_checkpoint.json", "w") as f:
                json.dump(state, f, indent=2)
            logger.info("🔖 State checkpointed successfully.")
        except Exception as e:
            logger.error(f"🚨 Failed to checkpoint state: {e}")

if __name__ == "__main__":
    orch = AdvancedOrchestrator()
    orch.run()
