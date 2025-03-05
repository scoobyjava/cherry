class Task:
    def __init__(self, name, func, dependencies=None):
        self.name = name
        self.func = func
        self.dependencies = dependencies if dependencies else []

    def run(self):
        self.func()
