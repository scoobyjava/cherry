from typing import Dict, Any, List
import openai
import os

from agents.base import Agent

class ResearcherAgent(Agent):
    """
    Agent responsible for researching and gathering information.
    """
    
    def __init__(self):
        super().__init__("Researcher")
        # Initialize OpenAI client
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        if self.api_key:
            openai.api_key = self.api_key
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Research a topic and return findings."""
        query = task.get("query", "")
        if not query:
            return {"error": "No query provided"}
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a research assistant. Provide detailed, accurate information on the topic."},
                    {"role": "user", "content": f"Research the following topic and provide a comprehensive summary: {query}"}
                ]
            )
            return {
                "findings": response.choices[0].message.content,
                "status": "success"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        return ["research", "information gathering", "topic analysis"]
