import importlib
import os

class AgentFactory:
    _agents = {}

    @classmethod
    def register_agent(cls, agent_name, agent_class):
        cls._agents[agent_name] = agent_class

    @classmethod
    def get_agent(cls, agent_name, *args, **kwargs):
        agent_class = cls._agents.get(agent_name)
        if not agent_class:
            raise ValueError(f"Agent '{agent_name}' not found")
        return agent_class(*args, **kwargs)

    @classmethod
    def load_agents(cls, agents_directory):
        for filename in os.listdir(agents_directory):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                module = importlib.import_module(f"agents.{module_name}")
                if hasattr(module, "register"):
                    module.register(cls)
