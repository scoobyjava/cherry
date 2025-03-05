import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import sys
import os
from contextlib import contextmanager

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.vector_store_fallback import (
    fallback_retrieve_from_postgres,
    get_embedding,
    load_config,
    get_connection_params
)

class TestVectorStoreFallback(unittest.TestCase):
    
    @patch('src.utils.vector_store_fallback.load_config')
    def test_get_connection_params(self, mock_load_config):
        mock_load_config.return_value = {
            'postgres': {
                'host': '${SECRET:POSTGRES_HOST}',
                'port': 5432,
                'database': '${SECRET:POSTGRES_DB}',
                'user': '${SECRET:POSTGRES_USER}',
                'password': '${SECRET:POSTGRES_PASSWORD}'
            }
        }
        
        with patch.dict('os.environ', {
            'POSTGRES_HOST': 'test-host',
            'POSTGRES_DB': 'test-db',
            'POSTGRES_USER': 'test-user',
            'POSTGRES_PASSWORD': 'test-password'
        }):
            params = get_connection_params()
            self.assertEqual(params['host'], 'test-host')
            self.assertEqual(params['port'], 5432)
            self.assertEqual(params['database'], 'test-db')
            self.assertEqual(params['user'], 'test-user')
            self.assertEqual(params['password'], 'test-password')
    
    @patch('src.utils.vector_store_fallback.openai')
    @patch('src.utils.vector_store_fallback.load_config')
    def test_get_embedding(self, mock_load_config, mock_openai):
        mock_load_config.return_value = {
            'openai': {
                'api_key': '${SECRET:OPENAI_API_KEY}'
            }
        }
        
        mock_embedding = [0.1, 0.2, 0.3]
        mock_openai.Embedding.create.return_value = {
            'data': [{'embedding': mock_embedding}]
        }
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            embedding = get_embedding("test query")
            self.assertEqual(embedding, mock_embedding)
            mock_openai.Embedding.create.assert_called_once()
    
    @patch('src.utils.vector_store_fallback.get_embedding')
    @patch('src.utils.vector_store_fallback.psycopg2.connect')
    @patch('src.utils.vector_store_fallback.get_connection_params')
    def test_fallback_retrieve_from_postgres(self, mock_get_params, mock_connect, mock_get_embedding):
        # Setup mocks
        mock_get_params.return_value = {'host': 'test-host', 'port': 5432}
        mock_embedding = [0.1, 0.2, 0.3]
        mock_get_embedding.return_value = mock_embedding
        
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Mock DB results
        mock_cursor.fetchall.return_value = [
            {'content': 'Result 1', 'metadata': {'id': '1'}, 'similarity_score': 0.95},
            {'content': 'Result 2', 'metadata': {'id': '2'}, 'similarity_score': 0.85}
        ]
        
        # Call function
        results = fallback_retrieve_from_postgres("test query", 2, "search_agent")
        
        # Assertions
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['content'], 'Result 1')
        self.assertEqual(results[0]['similarity'], 0.95)
        self.assertEqual(results[1]['content'], 'Result 2')
        
        # Verify correct table was queried
        execute_args = mock_cursor.execute.call_args[0]
        self.assertIn('search_vectors', execute_args[0])
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
