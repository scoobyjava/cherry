import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.agent_memory_sharing import share_memory_between_agents, validate_agents, load_config

class TestAgentMemorySharing(unittest.TestCase):
    
    @patch('utils.agent_memory_sharing.load_config')
    def test_validate_agents(self, mock_load_config):
        mock_config = {
            "pinecone": {
                "namespaces": {
                    "search_agent": {},
                    "recommendation_agent": {},
                    "qa_agent": {}
                }
            }
        }
        mock_load_config.return_value = mock_config
        
        # Test with valid agents
        self.assertTrue(validate_agents(mock_config, "search_agent", "qa_agent"))
        
        # Test with invalid source agent
        self.assertFalse(validate_agents(mock_config, "invalid_agent", "qa_agent"))
        
        # Test with invalid target agent
        self.assertFalse(validate_agents(mock_config, "search_agent", "invalid_agent"))
    
    @patch('utils.agent_memory_sharing.initialize_pinecone')
    @patch('utils.agent_memory_sharing.get_db_connection')
    @patch('utils.agent_memory_sharing.generate_embedding')
    @patch('utils.agent_memory_sharing.load_config')
    def test_share_memory_between_agents(self, mock_load_config, mock_generate_embedding, 
                                        mock_get_db_connection, mock_initialize_pinecone):
        # Mock configuration
        mock_config = {
            "pinecone": {
                "namespaces": {
                    "search_agent": {
                        "metadata_schema": {
                            "source_type": "string",
                            "timestamp": "number",
                            "relevance_score": "number",
                            "category": "string"
                        }
                    },
                    "qa_agent": {
                        "metadata_schema": {
                            "document_id": "string",
                            "section_id": "string",
                            "confidence": "number",
                            "last_updated": "number"
                        }
                    }
                }
            }
        }
        mock_load_config.return_value = mock_config
        
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
        
        # Mock embedding generation
        mock_generate_embedding.return_value = [0.1, 0.2, 0.3]
        
        # Mock Pinecone index
        mock_index = MagicMock()
        mock_initialize_pinecone.return_value = mock_index
        
        # Test sharing memory
        result = share_memory_between_agents(
            source_agent="search_agent",
            target_agent="qa_agent",
            content="This is important information for the QA system.",
            metadata={"relevance_score": 0.95}
        )
        
        # Check that the function executed database operations
        self.assertTrue(mock_cursor.execute.called)
        self.assertTrue(mock_conn.commit.called)
        
        # Check that the function called Pinecone
        self.assertTrue(mock_index.upsert.called)
        
        # Check result
        self.assertTrue(result["success"])
        self.assertEqual(result["source_agent"], "search_agent")
        self.assertEqual(result["target_agent"], "qa_agent")
        self.assertIn("postgres", result["stored_in"])
        self.assertIn("pinecone", result["stored_in"])

if __name__ == '__main__':
    unittest.main()
