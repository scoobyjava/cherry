"""Tests for the knowledge search module."""

import unittest
from unittest.mock import patch
from datetime import datetime, timedelta

from src.utils.knowledge_search import (
    search_knowledge, _call_sourcegraph_api, 
    _cache_result, _get_cached_result,
    _query_cache, _cache_expiry
)


class TestKnowledgeSearch(unittest.TestCase):
    """Test cases for the knowledge search functionality."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Clear the cache before each test
        _query_cache.clear()
        _cache_expiry.clear()
    
    def test_search_with_results(self):
        """Test search with a query that should return results."""
        query = "authentication in Cherry"
        result = search_knowledge(query)
        self.assertIn("auth.py", result)
        self.assertIn("middleware.py", result)
        self.assertIn("JWT token", result)
    
    def test_search_no_results(self):
        """Test search with a query that should return no results."""
        query = "something that doesn't exist"
        result = search_knowledge(query)
        self.assertIn("No results found", result)
    
    def test_caching(self):
        """Test that results are properly cached."""
        query = "authentication in Cherry"
        
        # First call should hit the API
        first_result = search_knowledge(query)
        
        # Mock the API to return different results
        with patch('src.utils.knowledge_search._call_sourcegraph_api') as mock_api:
            mock_api.return_value = [{"path": "different.py", "content": "different content"}]
            
            # Second call should use the cache
            second_result = search_knowledge(query)
            
            # The mock shouldn't have been called
            mock_api.assert_not_called()
            
            # Results should be the same
            self.assertEqual(first_result, second_result)
    
    def test_cache_expiration(self):
        """Test that cached results expire correctly."""
        query = "authentication in Cherry"
        
        # Cache a result but set it to expire immediately
        _cache_result(query, "Cached result")
        _cache_expiry[query.lower().strip()] = datetime.now() - timedelta(seconds=1)
        
        # Mock the API to return specific results
        with patch('src.utils.knowledge_search._call_sourcegraph_api') as mock_api:
            mock_api.return_value = [{"path": "new.py", "content": "new content"}]
            
            # Call should not use expired cache
            result = search_knowledge(query)
            
            # The mock should have been called
            mock_api.assert_called_once()
            
            # Result should contain the new content
            self.assertIn("new.py", result)
    
    def test_error_handling(self):
        """Test that errors are handled gracefully."""
        # Mock the API to raise an exception
        with patch('src.utils.knowledge_search._call_sourcegraph_api') as mock_api:
            mock_api.side_effect = Exception("API Error")
            
            result = search_knowledge("test query")
            
            # Should return a graceful error message
            self.assertIn("Unable to retrieve information", result)


if __name__ == '__main__':
    unittest.main()