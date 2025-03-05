import unittest
import time
from cherry.memory.manager import MemoryManager

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        # Set up a memory manager with Pinecone as primary and ChromaDB as cache
        primary_config = {"index_name": "cherry-test"}
        cache_config = {"collection_name": "memory-cache"}
        
        self.manager = MemoryManager(
            primary_provider="pinecone",
            primary_config=primary_config,
            cache_provider="chroma",
            cache_config=cache_config,
            cache_ttl=60  # Short TTL for testing
        )
        
    def test_store_and_retrieve(self):
        # Test storing and retrieving with manager
        data = {
            "content": "This is important information about machine learning algorithms",
            "metadata": {"source": "research-paper", "importance": "high"}
        }
        
        # Store data
        key = self.manager.store(data)
        self.assertIsNotNone(key)
        
        # Retrieve data
        results = self.manager.retrieve("machine learning")
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("content", results[0])
        
    def test_smart_ranking(self):
        # Store items with different importance and timestamps
        self.manager.store({
            "content": "Relevant but old and low importance",
            "metadata": {"importance": "low"},
            "timestamp": int(time.time()) - 86400*5  # 5 days old
        })
        
        self.manager.store({
            "content": "Relevant and new but medium importance",
            "metadata": {"importance": "medium"},
            "timestamp": int(time.time()) - 3600  # 1 hour old
        })
        
        self.manager.store({
            "content": "Relevant and high importance but slightly older",
            "metadata": {"importance": "high"},
            "timestamp": int(time.time()) - 43200  # 12 hours old
        })
        
        # Retrieve with smart ranking
        results = self.manager.retrieve("Relevant", recency_bias=0.3)
        
        # High importance should be first despite being older than medium importance
        self.assertIn("high", results[0].get("metadata", {}).get("importance", ""))
