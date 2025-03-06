from agent_interface import AgentInterface


class NLPAgent(AgentInterface):
    def __init__(self):
        super().__init__("NLPAgent")

    def start(self):
        print(f"{self.name} started. Ready to process language.")

    def handle_message(self, message: dict) -> dict:
        # A simple echo transformation for demonstration.
        command = message.get("command", "")
        response = f"{self.name} received command: {command}"
        return {"sender": self.name, "response": response}

    def stop(self):
        print(f"{self.name} stopping.")
