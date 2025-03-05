import asyncio
from typing import Dict, Any
from cherry.agents.base_agent import Agent
from cherry.utils.logger import logger
from cherry.utils.config import Config

class CodeAgent(Agent):
    """Agent specialized in code generation and software development tasks."""

    def __init__(self):
        super().__init__(
            name="Code Agent",
            description="Specialized in generating code and solving programming problems"
        )
        self.capabilities = ["code", "program", "develop", "script", "function", "algorithm", "debug"]

    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        requirement = task_data.get("description", "")
        logger.info(f"💻 {self.name} generating code for: {requirement}")
        try:
            await asyncio.sleep(0.1)  # Simulate async operation
            result = {
                "agent": self.name,
                "result": f"Generated Python code for: {requirement}",
                "language": "python"
            }
            return result
        except Exception as e:
            logger.error(f"{self.name} encountered an error: {e}")
            return {"agent": self.name, "error": str(e)}
