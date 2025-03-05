import queue
import threading

class TaskQueue:
    def __init__(self, num_workers=4):
        self.tasks = queue.Queue()
        self.num_workers = num_workers
        self.workers = []
        self._initialize_workers()

    def _initialize_workers(self):
        for _ in range(self.num_workers):
            worker = threading.Thread(target=self._worker)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

    def _worker(self):
        while True:
            task, args, kwargs = self.tasks.get()
            try:
                task(*args, **kwargs)
            finally:
                self.tasks.task_done()

    def add_task(self, task, *args, **kwargs):
        self.tasks.put((task, args, kwargs))

    def wait_completion(self):
        self.tasks.join()
