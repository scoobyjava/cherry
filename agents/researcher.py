from typing import Dict, Any, List, Optional
import aiohttp
import asyncio

from agents.base import BaseAgent
from cherry.core.messaging import MessagingSystem

class ResearcherAgent(BaseAgent):
    """
    Agent responsible for researching and gathering information.
    """
    
    def __init__(self, name, messaging_system):
        super().__init__(name, messaging_system)
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        if self.api_key:
            openai.api_key = self.api_key
        self.messaging_system.subscribe(self, 'research')
        self.sources = config.get('sources', []) if config else []
        self.session = None
    
    async def initialize(self) -> None:
        """Initialize the HTTP session for making requests."""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process research requests, fetching and analyzing information."""
        if 'query' not in request:
            return {"status": "error", "message": "Query is required"}
        
        query = request['query']
        search_results = await self.search(query)
        analysis = await self.analyze_results(search_results)
        
        return {
            "status": "success",
            "results": search_results,
            "analysis": analysis,
            "agent_id": self.agent_id
        }
    
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for information based on the query."""
        # Implement search functionality
        # This is a placeholder
        await asyncio.sleep(1)  # Simulate search time
        return [{"title": f"Result for {query}", "content": "Sample content"}]
    
    async def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the search results and extract insights."""
        # Implement analysis functionality
        # This is a placeholder
        await asyncio.sleep(0.5)  # Simulate analysis time
        return {"summary": "Analysis of results", "key_points": ["Point 1", "Point 2"]}
    
    def get_capabilities(self) -> List[str]:
        return ["research", "information gathering", "topic analysis"]

    @classmethod
    def register(cls, factory):
        super().register(factory)

    def perform_research(self):
        # Example of sending a message
        self.send_message('research', f"{self.name} is performing research")

    def receive_message(self, message_type, message):
        if message_type == 'research':
            print(f"Researcher {self.name} received research message: {message}")
        else:
            super().receive_message(message_type, message)

    def perform_task(self):
        # Implement the task logic here
        print("Researcher is performing a task.")

    def get_status(self):
        # Implement the status logic here
        return "Researcher is idle."

    def process(self, request: Dict[str, Any], memories: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Process a research request using available memories."""
        query = request["query"]
        
        # Format memories as context
        context = self._format_memories_as_context(memories or [])
        
        # In a real implementation, this might call an LLM or other tool
        # For this example, we'll just return a simple response
        response = f"I researched: {query}\n\n"
        response += f"Using context: {context}\n\n"
        response += "Here are my findings: This is a simulated research response."
        
        return {
            "content": response,
            "source": "researcher_agent"
        }

# Register the agent with the factory
def register(factory):
    ResearcherAgent.register(factory)
