
class Task:
    def __init__(self, name, handler):
        self.name = name
        self.handler = handler

TASKS = [
    Task("task1", "handle_task1"),
    Task("task2", "handle_task2"),
    # Add more tasks as needed
]
