import asyncio
import logging

logger = logging.getLogger(__name__)


class TaskQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self._shutdown = asyncio.Event()

    async def add_task(self, coro, retries=3, retry_delay=1, *args, **kwargs):
        # Enqueue a task with its parameters and retry settings.
        await self.queue.put({
            "coro": coro,
            "args": args,
            "kwargs": kwargs,
            "retries": retries,
            "retry_delay": retry_delay,
        })

    async def worker(self):
        while not self._shutdown.is_set():
            task = await self.queue.get()
            try:
                await task["coro"](*task["args"], **task["kwargs"])
            except Exception as e:
                if task["retries"] > 0:
                    logger.warning(
                        f"Task failed: {e}. Retrying in {task['retry_delay']} seconds..."
                    )
                    await asyncio.sleep(task["retry_delay"])
                    task["retries"] -= 1
                    task["retry_delay"] *= 2  # Exponential backoff
                    await self.queue.put(task)
                else:
                    logger.error(f"Task failed after retries: {e}")
            finally:
                self.queue.task_done()

    async def process_tasks(self, num_workers=1):
        # Start worker tasks to process the queue.
        workers = [asyncio.create_task(self.worker())
                   for _ in range(num_workers)]
        await self.queue.join()
        self._shutdown.set()
        for w in workers:
            w.cancel()
        await asyncio.gather(*workers, return_exceptions=True)
