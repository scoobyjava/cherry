from agents.researcher import ResearchAgent
from agents.code_agent import CodeAgent  # Import the new code agent

class Orchestrator:
    
    def _init_agents(self):
        """Initialize all agents."""
        self.agents = {}
        
        # Initialize the code agent
        self.agents["code"] = CodeAgent(self.config, self.llm)
    
    async def route_message(self, message, context=None):
        """Route a message to the appropriate agent."""
        
        # Check if this is a code-related request
        if any(keyword in message.lower() for keyword in [
            "code", "program", "function", "class", "bug", "error",
            "implement", "develop", "script", "syntax", "algorithm"
        ]):
            self.logger.info("Routing request to code agent")
            return await self.agents["code"].process(message, context)
