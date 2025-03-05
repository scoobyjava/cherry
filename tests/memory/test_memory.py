import unittest
from cherry.memory.factory import get_memory_provider

class TestMemory(unittest.TestCase):
    def setUp(self):
        # Use a test namespace to avoid affecting production data
        self.memory = get_memory_provider("pinecone", index_name="cherry-test")
        
    def test_store_and_retrieve(self):
        # Test basic memory operations
        key = "test-memory-1"
        data = {
            "content": "This is a test memory about artificial intelligence",
            "metadata": {"source": "unit-test", "importance": "low"}
        }
        
        # Store data
        stored_key = self.memory.store(key, data)
        self.assertEqual(stored_key, key)
        
        # Retrieve data
        results = self.memory.retrieve("artificial intelligence")
        self.assertGreaterEqual(len(results), 1)

    def test_update(self):
        key = "test-update-memory"
        data = {
            "content": "Original test content",
            "metadata": {"source": "unit-test"}
        }
        
        # Store initial data
        self.memory.store(key, data)
        
        # Update data
        updated_data = {
            "content": "Updated test content",
            "metadata": {"source": "unit-test", "updated": True}
        }
        
        success = self.memory.update(key, updated_data)
        self.assertTrue(success)
        
        # Verify update
        results = self.memory.retrieve("Updated test")
        self.assertIn("Updated test content", results[0]["content"])
        
    def test_delete(self):
        key = "test-delete-memory"
        data = {
            "content": "Content to be deleted",
            "metadata": {"source": "unit-test"}
        }
        
        # Store data
        self.memory.store(key, data)
        
        # Delete data
        success = self.memory.delete(key)
        self.assertTrue(success)
