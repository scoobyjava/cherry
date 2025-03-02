import asyncio
import json
import time
import networkx as nx
from threading import Lock
from typing import Dict, Any, List
from dataclasses import dataclass, field

import openai
from config import Config
from logger import logger
from memory_chroma import ChromaMemory

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
        self.loop = asyncio.new_event_loop()

    def load_configuration(self, config_path: str):
        try:
            with open(config_path, 'r') as config_file:
                self.advanced_config = json.load(config_file)
        except FileNotFoundError:
            self.advanced_config = {
                "max_concurrent_tasks": 5,
                "task_timeout": 3600
            }

    def _init_memory_system(self):
        try:
            self.primary_memory = ChromaMemory(collection_name="cherry_primary_memory")
            logger.info("Memory initialized successfully.")
        except Exception as e:
            logger.error(f"Memory initialization failed: {e}")

    def run(self):
        self.running = True
        logger.info("AdvancedOrchestrator running...")

    def stop(self):
        self.running = False
        logger.info("AdvancedOrchestrator stopped.")

