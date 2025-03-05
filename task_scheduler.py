from task import Task

class TaskScheduler:
    def __init__(self):
        self.tasks = {}
        self.execution_order = []

    def add_task(self, task):
        self.tasks[task.name] = task

    def resolve_dependencies(self):
        visited = set()
        temp_mark = set()

        def visit(task):
            if task.name in visited:
                return
            if task.name in temp_mark:
                raise Exception("Circular dependency detected")
            temp_mark.add(task.name)
            for dep in task.dependencies:
                visit(self.tasks[dep])
            temp_mark.remove(task.name)
            visited.add(task.name)
            self.execution_order.append(task)

        for task in self.tasks.values():
            visit(task)

    def run(self):
        self.resolve_dependencies()
        for task in self.execution_order:
            task.run()
