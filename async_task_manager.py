import asyncio


class TaskManager:
    def __init__(self):
        # Initialize an asyncio queue to manage tasks
        self.queue = asyncio.Queue()

    async def worker(self):
        while True:
            task = await self.queue.get()
            try:
                # Execute the enqueued task, which should be an async callback
                await task()
            except Exception as e:
                print(f"Error processing task: {e}")
            self.queue.task_done()

    async def add_task(self, task):
        # Enqueue an async task
        await self.queue.put(task)

    async def run(self, workers=1):
        # Start worker coroutines to process tasks
        workers_tasks = [asyncio.create_task(
            self.worker()) for _ in range(workers)]
        await self.queue.join()
        for w in workers_tasks:
            w.cancel()
