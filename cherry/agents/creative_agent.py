import asyncio
from typing import Dict, Any
from cherry.agents.base_agent import Agent
from cherry.utils.logger import logger
from cherry.utils.config import Config

class CreativeAgent(Agent):
    """Agent specialized in creative content generation."""

    def __init__(self):
        super().__init__(
            name="Creative Agent",
            description="Specialized in generating creative content and ideas"
        )
        self.capabilities = ["write", "create", "generate", "design", "creative", "story", "content"]

    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = task_data.get("description", "")
        logger.info(f"🎨 {self.name} generating creative content for: {prompt}")
        try:
            await asyncio.sleep(0.1)  # Simulate async operation
            result = {
                "agent": self.name,
                "result": f"Creative content based on: {prompt}"
            }
            return result
        except Exception as e:
            logger.error(f"{self.name} encountered an error: {e}")
            return {"agent": self.name, "error": str(e)}
