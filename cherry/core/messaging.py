class MessagingSystem:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, agent, message_type):
        if message_type not in self.subscribers:
            self.subscribers[message_type] = []
        self.subscribers[message_type].append(agent)

    def unsubscribe(self, agent, message_type):
        if message_type in self.subscribers:
            self.subscribers[message_type].remove(agent)

    def publish(self, message_type, message):
        if message_type in self.subscribers:
            for agent in self.subscribers[message_type]:
                agent.receive_message(message_type, message)
