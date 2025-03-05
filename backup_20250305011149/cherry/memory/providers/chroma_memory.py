import chromadb
import os
import uuid
from typing import Dict, List, Any, Optional
from ..base import MemoryInterface
from ...utils.embeddings import get_embedding, get_embedding_dimension

class ChromaMemory(MemoryInterface):
    def __init__(self, collection_name: str, persist_directory: Optional[str] = None):
        # Initialize client - persistent or in-memory
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=None  # We'll handle embeddings manually
        )
    
    def store(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> str:
        # Generate embedding for the content
        content = data.get("content", "")
        vector = get_embedding(content)
        
        # Handle metadata - ChromaDB separates metadata from embeddings
        metadata = {k: v for k, v in data.items() if k != "content"}
        if namespace:
            metadata["namespace"] = namespace
            
        # Store in ChromaDB
        self.collection.add(
            ids=[key],
            embeddings=[vector],
            metadatas=[metadata],
            documents=[content]
        )
        return key
    
    def retrieve(self, query: str, namespace: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant memory entries based on semantic search"""
        # Generate embedding for the query
        query_vector = get_embedding(query)
        
        # Prepare query filters for namespace if specified
        where_clause = {"namespace": namespace} if namespace else None
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=limit,
            where=where_clause
        )
        
        # Format and return results
        entries = []
        for i in range(len(results["ids"][0])):
            entries.append({
                "content": results["documents"][0][i],
                **results["metadatas"][0][i]
            })
        
        return entries
    
    def update(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> bool:
        """Update existing memory entry"""
        try:
            # Generate embedding for the content
            content = data.get("content", "")
            vector = get_embedding(content)
            
            # Handle metadata - ChromaDB separates metadata from embeddings
            metadata = {k: v for k, v in data.items() if k != "content"}
            if namespace:
                metadata["namespace"] = namespace
                
            # Update in ChromaDB (requires delete+add)
            self.collection.update(
                ids=[key],
                embeddings=[vector],
                metadatas=[metadata],
                documents=[content]
            )
            return True
        except Exception as e:
            print(f"Error updating memory: {e}")
            return False
    
    def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        """Remove a memory entry"""
        try:
            # ChromaDB doesn't support namespace in delete operation directly
            # So we handle simple key-based deletion
            self.collection.delete(ids=[key])
            return True
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False