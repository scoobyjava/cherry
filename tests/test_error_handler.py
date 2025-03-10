"""
Unit tests for the error_handler module.
"""

import unittest
from src.utils.error_handler import capture_error, analyze_and_fix

class TestErrorHandler(unittest.TestCase):
    def test_index_error_fix(self):
        """Test that analyze_and_fix returns a safe fix for an IndexError."""
        task_id = "test_task_indexError"
        error_message = "list index out of range (IndexError)"
        # Simulate analysis of the error message.
        fixed_code = analyze_and_fix(task_id, error_message)
        # The fix suggestion should include the safe_access function and exception handling.
        self.assertIn("def safe_access", fixed_code)
        self.assertIn("except IndexError", fixed_code)

if __name__ == '__main__':
    unittest.main()

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContextMemory:
    def __init__(self):
        """
        Initialize the memory module with an empty dictionary for storing contexts
        and a TF-IDF vectorizer for embedding and similarity search.
        """
        self.contexts = {}  # Key-value store for contexts
        self.keys = []      # List of keys to maintain order
        self.vectorizer = TfidfVectorizer()

    def store_context(self, key: str, context: str):
        """
        Store a context in memory with a unique key.

        Args:
            key (str): A unique identifier for the context.
            context (str): The context or information to be stored.
        """
        if key in self.contexts:
            raise ValueError(f"Key '{key}' already exists in memory.")
        self.contexts[key] = context
        self.keys.append(key)

    def retrieve_context(self, query: str, top_k: int) -> list[str]:
        """
        Retrieve the most relevant contexts based on a query.

        Args:
            query (str): The query to search for relevant contexts.
            top_k (int): The number of most relevant contexts to return.

        Returns:
            list[str]: A list of the most relevant contexts.
        """
        if not self.contexts:
            return []

        # Combine all stored contexts into a list
        all_contexts = [self.contexts[key] for key in self.keys]

        # Fit the vectorizer on all stored contexts + the query
        combined_texts = all_contexts + [query]
        tfidf_matrix = self.vectorizer.fit_transform(combined_texts)

        # Compute cosine similarity between the query and all stored contexts
        query_vector = tfidf_matrix[-1]
        context_vectors = tfidf_matrix[:-1]
        
        similarities = cosine_similarity(query_vector, context_vectors).flatten()

        # Get indices of top_k most similar contexts
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        # Retrieve the corresponding keys and contexts
        retrieved_keys = [self.keys[i] for i in top_indices]
        return [self.contexts[key] for key in retrieved_keys]

    def clear_memory(self):
        """Clear all stored contexts."""
        self.contexts.clear()
        self.keys.clear()

Develop an error_handler.py module that automatically captures runtime errors from Cherry's executed code tasks. Implement methods such as capture_error(task_id: str, error: Exception) and analyze_and_fix(task_id: str, error_message: str) to analyze stack traces and suggest fixes automatically via the AI coding assistant. Simulate a scenario where Cherry runs a faulty code snippet, detects an error (like an IndexError), and successfully generates a corrected version of the code. Include detailed logging of error analysis steps and resolution outcomes