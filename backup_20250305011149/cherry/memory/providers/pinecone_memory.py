import pinecone
import os
from typing import Dict, List, Any, Optional
from ..base import MemoryInterface
from ...utils.embeddings import get_embedding

class PineconeMemory(MemoryInterface):
    def __init__(self, index_name: str):
        api_key = os.getenv("PINECONE_API_KEY")
        environment = os.getenv("PINECONE_ENVIRONMENT")
        
        pinecone.init(api_key=api_key, environment=environment)
        self.index = pinecone.Index(index_name)
        
    def store(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> str:
        # Generate embedding for the content
        content = data.get("content", "")
        vector = get_embedding(content)
        
        # Store in Pinecone
        self.index.upsert(
            vectors=[(key, vector, data)],
            namespace=namespace
        )
        return key
        
    def retrieve(self, query: str, namespace: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant memory entries based on semantic search"""
        # Generate embedding for the query
        query_vector = get_embedding(query)
        
        # Search in Pinecone
        results = self.index.query(
            vector=query_vector,
            top_k=limit,
            namespace=namespace,
            include_metadata=True
        )
        
        # Format and return results
        return [match['metadata'] for match in results.matches]
    
    def update(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> bool:
        """Update existing memory entry"""
        try:
            # Generate new embedding for updated content
            content = data.get("content", "")
            vector = get_embedding(content)
            
            # Update in Pinecone (upsert will create or update)
            self.index.upsert(
                vectors=[(key, vector, data)],
                namespace=namespace
            )
            return True
        except Exception as e:
            print(f"Error updating memory: {e}")
            return False
    
    def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        """Remove a memory entry"""
        try:
            self.index.delete(ids=[key], namespace=namespace)
            return True
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False