import asyncio
from agent_manager import AgentManager  # ...existing code...
from agents.researcher import ResearchAgent
from agents.code_agent import CodeAgent  # Import the new code agent


class Orchestrator:
    def __init__(self):
        # Mapping agent names to agent instances
        self.agents = {}

    def register_agent(self, agent):
        # Assuming each agent has a 'name' attribute and a 'callback' method.
        self.agents[agent.name] = agent

    def process_task(self, agent_name, task):
        """
        Route the task to the specified agent's callback.
        """
        if agent_name not in self.agents:
            raise ValueError(f"No agent registered with name: {agent_name}")
        agent = self.agents[agent_name]
        return agent.callback(task)

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


class TaskOrchestrator:
    def __init__(self, agent_capabilities: dict):
        """
        agent_capabilities: dict mapping agent names to their list of capabilities
        e.g., {"ExampleAgent": ["text_analysis", "task_delegation"]}
        """
        self.agent_capabilities = agent_capabilities
        self.agent_manager = AgentManager()  # ...existing code...

    def register_agents(self, agents):
        """
        agents: list of agent instances with attributes 'name' and method 'register'
        """
        for agent in agents:
            if agent.name in self.agent_capabilities:
                agent.register(self.agent_manager)

    async def delegate_task(self, task: dict):
        """
        task: dict with keys 'capability' and 'data'
        Auto-delegates the task to a suitable agent based on its capability.
        """
        capability = task.get("capability")
        if not capability:
            print("Task missing 'capability'")
            return

        # Identify agents with the required capability.
        matched_agents = [
            name for name, caps in self.agent_capabilities.items() if capability in caps]
        if not matched_agents:
            print(f"No agents available for capability: {capability}")
            return

        # For simplicity, pick the first candidate.
        agent_name = matched_agents[0]
        callback = self.agent_manager.agents.get(agent_name)
        if callback:
            await asyncio.to_thread(callback, task.get("data", ""))
        else:
            print(f"Agent callback not found for: {agent_name}")


# Example usage:
if __name__ == "__main__":
    async def main():
        # Define agents' capabilities.
        capabilities = {
            "ExampleAgent": ["text_analysis", "task_delegation"],
            # ...additional agents can be added here...
        }
        orchestrator = TaskOrchestrator(capabilities)
        from assist_ai import ExampleAgent  # ...existing code...
        agents = [ExampleAgent()]
        orchestrator.register_agents(agents)

        # Delegate a sample task.
        task = {"capability": "text_analysis",
                "data": "Analyze this sample text."}
        await orchestrator.delegate_task(task)

    asyncio.run(main())

    class DummyAgent:
        def __init__(self, name):
            self.name = name

        def callback(self, data):
            print(f"{self.name} processed task: {data}")

        def register(self, orchestrator):
            orchestrator.register_agent(self)

    orchestrator = Orchestrator()
    agent = DummyAgent("Agent1")
    agent.register(orchestrator)
    orchestrator.process_task("Agent1", {"info": "sample task"})
