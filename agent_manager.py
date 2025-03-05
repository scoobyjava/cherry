class AgentManager:
    def __init__(self):
        # Dictionary to store agents and their callbacks
        self.agents = {}

    def register_agent(self, agent_name, callback):
        self.agents[agent_name] = callback

    def initialize_agents(self, agents):
        # Expect each agent to implement a register(manager) method.
        for agent in agents:
            agent.register(self)
        return self.agents
