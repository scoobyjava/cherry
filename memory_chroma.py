import asyncio

class ChromaMemory:
    def __init__(self):
        self.vectors = {}  # Use a dictionary for efficient storage and retrieval

    def add_vector(self, key, vector):
        self.vectors[key] = vector

    def get_vector(self, key):
        return self.vectors.get(key)

    def remove_vector(self, key):
        # Ensure vectors are properly removed to avoid memory leaks
        if key in self.vectors:
            del self.vectors[key]

    def clear_memory(self):
        # Clear all vectors to free up memory
        self.vectors.clear()

    def __del__(self):
        # Ensure all resources are released when the object is destroyed
        self.clear_memory()

async def memory_chroma_async_function():
    try:
        await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("Task was cancelled")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
