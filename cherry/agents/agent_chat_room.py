# ...existing code (if any)...

class AgentChatRoom:
    def __init__(self):
        # Holds agents by their name
        self.agents = {}
        self.messages = []

    def add_agent(self, agent):
        """Register an agent to the chat room"""
        self.agents[agent.name] = agent

    def assign_task(self, agent_name: str, task: str):
        """Cherry, the moderator, assigns a task to an agent"""
        message = f"Cherry assigns task '{task}' to agent {agent_name}."
        self.messages.append(message)
        print(message)

    def collect_updates(self):
        """Collects task updates from each agent using their speak() method"""
        for agent in self.agents.values():
            update = agent.speak("has completed their assigned task update.")
            self.messages.append(update)
            print(update)

    def summarize(self):
        """Cherry summarizes all the updates from the chat"""
        summary = "Chat Summary:\n" + "\n".join(self.messages)
        print(summary)
        return summary


# Example usage (for testing):
if __name__ == "__main__":
    # Dummy agent implementation with a speak() method.
    class DummyAgent:
        def __init__(self, name):
            self.name = name

        def speak(self, update):
            return f"{self.name} says: {update}"

    chat_room = AgentChatRoom()
    # Create agents
    agent1 = DummyAgent("AgentOne")
    agent2 = DummyAgent("AgentTwo")
    # Add agents to chat room
    chat_room.add_agent(agent1)
    chat_room.add_agent(agent2)
    # Cherry assigns tasks
    chat_room.assign_task("AgentOne", "Review PR #42")
    chat_room.assign_task("AgentTwo", "Merge branch 'feature/update'")
    # Collect updates from agents
    chat_room.collect_updates()
    # Summarize the chat
    chat_room.summarize()
