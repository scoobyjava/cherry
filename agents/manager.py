from .researcher import ResearcherAgent

class AgentManager:
    def __init__(self):
        self.agents = []

    def create_agent(self, agent_type):
        if agent_type == "researcher":
            agent = ResearcherAgent()
            self.agents.append(agent)
            return agent
        else:
            raise ValueError("Unknown agent type")

    def manage_agents(self):
        for agent in self.agents:
            agent.perform_task()
            print(agent.get_status())
