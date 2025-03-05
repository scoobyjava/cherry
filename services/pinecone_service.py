import os
import logging
import pinecone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self, config: Dict[str, Any]):
        """Initialize Pinecone service with config"""
        self.config = config
        
        # Process API key that might be a reference to a secret
        api_key = self._process_config_value(config["api_key"])
        
        # Initialize Pinecone client
        pinecone.init(api_key=api_key, environment=config["environment"])
        
        # Connect to the specified index
        self.index_name = config["index_name"]
        self.index = pinecone.Index(self.index_name)
        
        logger.info(f"Initialized Pinecone service with index: {self.index_name}")
    
    def _process_config_value(self, value: str) -> str:
        """Process configuration values that might contain references to secrets"""
        if value.startswith("${SECRET:") and value.endswith("}"):
            secret_name = value[9:-1]
            return os.environ.get(secret_name, "")
        return value
    
    def list_vectors(self, namespace: str) -> List[str]:
        """List all vector IDs in a namespace"""
        try:
            # Pinecone doesn't have a direct "list all vectors" API
            # We need to use a workaround like fetching stats or querying with a dummy vector
            stats = self.index.describe_index_stats()
            
            # For more detailed implementation, we would need to query vectors in batches
            # This is a simplified placeholder - in a real implementation,
            # we might need to keep track of IDs in a separate database table
            
            # For now, return an empty list to indicate "check all entries"
            # In a real implementation, we would fetch actual IDs
            return []
        except Exception as e:
            logger.error(f"Error listing vectors from Pinecone: {str(e)}")
            return []
    
    def upsert_vectors(self, namespace: str, vectors: List[Dict[str, Any]]) -> bool:
        """Upsert vectors to Pinecone"""
        try:
            # Format vectors for Pinecone
            pinecone_vectors = []
            for v in vectors:
                pinecone_vectors.append({
                    "id": v["id"],
                    "values": v["values"],
                    "metadata": v.get("metadata", {})
                })
            
            # Upsert in batches to avoid API limits
            batch_size = 100
            for i in range(0, len(pinecone_vectors), batch_size):
                batch = pinecone_vectors[i:i+batch_size]
                self.index.upsert(vectors=batch, namespace=namespace)
                
            logger.info(f"Upserted {len(vectors)} vectors to namespace '{namespace}'")
            return True
        except Exception as e:
            logger.error(f"Error upserting vectors to Pinecone: {str(e)}")
            return False
    
    def query_vectors(self, namespace: str, vector: List[float], top_k: int = 5, 
                      filter_dict: Optional[Dict] = None) -> List[Dict]:
        """Query vectors in Pinecone"""
        try:
            # Default to the namespace top_k if not specified
            if top_k is None and namespace in self.config["namespaces"]:
                top_k = self.config["namespaces"][namespace].get("default_top_k", 5)
            
            results = self.index.query(
                namespace=namespace,
                vector=vector,
                top_k=top_k,
                include_values=True,
                include_metadata=True,
                filter=filter_dict
            )
            
            return results.get("matches", [])
        except Exception as e:
            logger.error(f"Error querying vectors from Pinecone: {str(e)}")
            return []
