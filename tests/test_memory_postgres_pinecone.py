import os
import unittest
import numpy as np
from unittest.mock import patch, MagicMock
from cherry.memory.postgres_pinecone import PostgresPineconeMemory

class TestPostgresPineconeMemory(unittest.TestCase):
    """Test the PostgreSQL and Pinecone memory integration."""
    
    def setUp(self):
        """Set up test environment with mocks for external dependencies."""
        # Mock the PostgreSQL connection
        self.psycopg2_connect_patcher = patch('cherry.memory.postgres_pinecone.psycopg2.connect')
        self.mock_psycopg2_connect = self.psycopg2_connect_patcher.start()
        
        # Create mock connection and cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value.__enter__.return_value = self.mock_cursor
        self.mock_psycopg2_connect.return_value = self.mock_conn
        
        # Mock Pinecone
        self.pinecone_init_patcher = patch('cherry.memory.postgres_pinecone.pinecone.init')
        self.mock_pinecone_init = self.pinecone_init_patcher.start()
        
        self.pinecone_list_indexes_patcher = patch('cherry.memory.postgres_pinecone.pinecone.list_indexes')
        self.mock_pinecone_list_indexes = self.pinecone_list_indexes_patcher.start()
        self.mock_pinecone_list_indexes.return_value = ["test-index"]
        
        self.pinecone_index_patcher = patch('cherry.memory.postgres_pinecone.pinecone.Index')
        self.mock_pinecone_index = self.pinecone_index_patcher.start()
        self.mock_index = MagicMock()
        self.mock_pinecone_index.return_value = self.mock_index
        
        # Initialize memory system
        self.memory = PostgresPineconeMemory(
            postgres_connection_string="postgresql://fake:fake@localhost/fake",
            pinecone_api_key="fake-api-key",
            pinecone_environment="us-west1-gcp",
            pinecone_index_name="test-index"
        )
    
    def tearDown(self):
        """Clean up mocks."""
        self.psycopg2_connect_patcher.stop()
        self.pinecone_init_patcher.stop()
        self.pinecone_list_indexes_patcher.stop()
        self.pinecone_index_patcher.stop()
    
    def test_store_and_retrieve_memory(self):
        """
        Test that a memory can be stored and immediately retrieved.
        This test verifies the end-to-end functionality of the memory system.
        """
        # Test data
        test_content = "This is a test memory about artificial intelligence"
        test_embedding = [0.1] * 1536  # 1536-dimensional embedding
        test_metadata = {"source": "unit test", "topic": "AI"}
        
        # Generate a UUID for our memory (for mocking purposes)
        test_memory_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Mock UUID generation to return a predictable ID
        with patch('cherry.memory.postgres_pinecone.uuid.uuid4', return_value=test_memory_id):
            # Store memory
            memory_id = self.memory.store_memory(
                content=test_content,
                embedding=test_embedding,
                metadata=test_metadata
            )
            
            # Verify memory ID
            self.assertEqual(memory_id, str(test_memory_id))
            
            # Verify PostgreSQL interaction
            self.mock_cursor.execute.assert_called()
            self.mock_conn.commit.assert_called()
            
            # Verify Pinecone interaction
            self.mock_index.upsert.assert_called_once()
            
            # Create expected query results from Pinecone
            expected_query_result = {
                'matches': [
                    {
                        'id': str(test_memory_id),
                        'score': 0.95,  # Simulated similarity score
                        'metadata': {'content': test_content[:100], **test_metadata}
                    }
                ]
            }
            self.mock_index.query.return_value = expected_query_result
            
            # Mock PostgreSQL fetch for retrieval
            self.mock_cursor.fetchone.return_value = (
                test_content,  # content
                test_metadata,  # metadata
                "2023-03-01T12:00:00"  # created_at
            )
            
            # Test retrieval
            query_embedding = [0.2] * 1536  # Slightly different embedding
            retrieved_memories = self.memory.retrieve_memories(
                query_embedding=query_embedding,
                limit=1
            )
            
            # Verify Pinecone query was called
            self.mock_index.query.assert_called_once_with(
                vector=query_embedding,
                top_k=1,
                include_metadata=True
            )
            
            # Verify PostgreSQL was queried for the memory details
            self.mock_cursor.execute.assert_called()
            
            # Verify the retrieved memory
            self.assertEqual(len(retrieved_memories), 1)
            retrieved_memory = retrieved_memories[0]
            self.assertEqual(retrieved_memory['id'], str(test_memory_id))
            self.assertEqual(retrieved_memory['content'], test_content)
            self.assertEqual(retrieved_memory['metadata'], test_metadata)
            self.assertEqual(retrieved_memory['score'], 0.95)

if __name__ == '__main__':
    unittest.main()
