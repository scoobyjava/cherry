class AgentInterface:
    """
    Base class for all agents. Each agent must implement these methods.
    """

    def __init__(self, name: str):
        self.name = name

    def start(self):
        """Start the agent and initialize resources."""
        raise NotImplementedError

    def handle_message(self, message: dict) -> dict:
        """
        Process an incoming message and return a response.
        Example message structure: {"sender": "AgentX", "command": "do_task", "payload": ...}
        """
        raise NotImplementedError

    def stop(self):
        """Gracefully stop the agent."""
        raise NotImplementedError
