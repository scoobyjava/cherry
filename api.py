import asyncio

# ...existing code...

async def api_async_function():
    try:
        # ...existing code...
        await asyncio.sleep(1)
        # ...existing code...
    except asyncio.CancelledError:
        print("Task was cancelled")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")

# ...existing code...
