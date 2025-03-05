from typing import Dict
from .base_agent import BaseAgent

class AIAgent(BaseAgent):
    def handle_task(self, task: str) -> str:
        # Retrieve relevant context from memory
        context_entries = self.memory_manager.retrieve(task, limit=3)
        
        # Combine the context into a single string (simplified demonstration)
        context_summary = "\n".join([x.get("content", "") for x in context_entries])
        
        # Simple example: store new content or update memory based on the task
        new_data: Dict[str, Any] = {
            "content": f"Agent response for '{task}'",
            "metadata": {"importance": "medium"}
        }
        self.memory_manager.store(new_data)
        
        # Return a mocked response using the retrieved context
        return f"Responding to '{task}' with context:\n{context_summary}"