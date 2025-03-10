"""
Unit tests for the context_memory module.
"""

import unittest
from src.utils.context_memory import store_context, retrieve_context, _memory_store


class TestContextMemory(unittest.TestCase):
    def setUp(self):
        # Clear the memory store before each test
        _memory_store.clear()

    def test_store_and_retrieve_context(self):
        # Store several contexts
        store_context("task1", "Implemented code validation for Cherry")
        store_context("task2", "Fixed bug in API integration")
        store_context("task3", "Added feature to task orchestrator")

        # Retrieve contexts for a query that should match task1
        results = retrieve_context("code validation", top_k=2)
        self.assertTrue(
            any("code validation" in context for context in results))

        # Retrieve contexts for a query that should match task2
        results = retrieve_context("bug", top_k=1)
        self.assertTrue(any("bug" in context for context in results))

    def test_top_k_retrieval(self):
        # Store three contexts
        store_context("a", "Context A")
        store_context("b", "Context B")
        store_context("c", "Context C")

        # Retrieve with top_k=2
        results = retrieve_context("Context", top_k=2)
        self.assertEqual(len(results), 2)


if __name__ == "__main__":
    unittest.main()
