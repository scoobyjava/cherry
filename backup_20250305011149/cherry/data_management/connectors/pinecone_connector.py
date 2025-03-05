"""
Connector for Pinecone vector database.
"""
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

import pinecone

from logger import get_logger

logger = get_logger(__name__)

class PineconeConnector:
    """Connector for Pinecone vector database."""
    
    def __init__(self, api_key: Optional[str] = None, environment: Optional[str] = None):
        """
        Initialize Pinecone connector.
        
        Args:
            api_key: Pinecone API key. If None, will try to get from environment variables.
            environment: Pinecone environment. If None, will try to get from environment variables.
        """
        self.api_key = api_key or os.environ.get("PINECONE_API_KEY")
        self.environment = environment or os.environ.get("PINECONE_ENVIRONMENT")
        
        if not self.api_key:
            raise ValueError("Pinecone API key is required")
        if not self.environment:
            raise ValueError("Pinecone environment is required")
            
        pinecone.init(api_key=self.api_key, environment=self.environment)
        
    def get_index(self, index_name: str):
        """
        Get Pinecone index.
        
        Args:
            index_name: Name of the index.
            
        Returns:
            Pinecone index.
        """
        try:
            return pinecone.Index(index_name)
        except Exception as e:
            logger.error(f"Error getting Pinecone index {index_name}: {e}")
            raise
            
    def find_vectors_older_than(self, index_name: str, months: int = 6) -> List[str]:
        """
        Find vectors older than a specified number of months.
        
        Args:
            index_name: Name of the index.
            months: Number of months.
            
        Returns:
            List of vector IDs older than the specified months.
        """
        index = self.get_index(index_name)
        cutoff_date = datetime.now() - timedelta(days=30*months)
        cutoff_timestamp = int(cutoff_date.timestamp())
        
        # Query vectors with timestamp metadata
        # Note: This assumes vectors have a 'timestamp' or 'created_at' field in metadata
        try:
            # First get vector count to determine batching approach
            stats = index.describe_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            
            vector_ids = []
            # Use fetch with filter or query with filter depending on Pinecone version
            # This is a simplified approach - actual implementation will depend on your Pinecone setup
            
            # Example: Using metadata filtering if available
            old_vectors = index.query(
                vector=[0] * 1536,  # Placeholder vector
                filter={"timestamp": {"$lt": cutoff_timestamp}},
                top_k=10000,
                include_metadata=True
            )
            
            for match in old_vectors.matches:
                vector_ids.append(match.id)
                
            logger.info(f"Found {len(vector_ids)} vectors older than {months} months in {index_name}")
            return vector_ids
            
        except Exception as e:
            logger.error(f"Error finding old vectors in {index_name}: {e}")
            raise
    
    def fetch_vectors_by_ids(self, index_name: str, vector_ids: List[str]) -> Dict[str, Any]:
        """
        Fetch vectors by IDs.
        
        Args:
            index_name: Name of the index.
            vector_ids: List of vector IDs.
            
        Returns:
            Dictionary of vectors with their metadata.
        """
        index = self.get_index(index_name)
        
        try:
            # Fetch vectors in batches to avoid hitting API limits
            batch_size = 100
            all_vectors = {}
            
            for i in range(0, len(vector_ids), batch_size):
                batch_ids = vector_ids[i:i+batch_size]
                fetch_response = index.fetch(ids=batch_ids)
                all_vectors.update(fetch_response.vectors)
                
            return all_vectors
            
        except Exception as e:
            logger.error(f"Error fetching vectors by IDs from {index_name}: {e}")
            raise
    
    def delete_vectors(self, index_name: str, vector_ids: List[str]) -> bool:
        """
        Delete vectors by IDs.
        
        Args:
            index_name: Name of the index.
            vector_ids: List of vector IDs.
            
        Returns:
            True if successful, False otherwise.
        """
        index = self.get_index(index_name)
        
        try:
            # Delete in batches
            batch_size = 100
            for i in range(0, len(vector_ids), batch_size):
                batch_ids = vector_ids[i:i+batch_size]
                index.delete(ids=batch_ids)
                
            logger.info(f"Successfully deleted {len(vector_ids)} vectors from {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors from {index_name}: {e}")
            return False
