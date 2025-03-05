import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import numpy as np
import os
from typing import List, Dict, Any, Optional, Union

class VectorStore:
    """
    Vector store implementation using ChromaDB with HNSW indexing for fast 
    semantic search with cosine similarity.
    """
    
    def __init__(
        self, 
        collection_name: str = "default_collection",
        persist_directory: str = "./chroma_db", 
        embedding_function = None,
        distance_function: str = "cosine"
    ):
        """
        Initialize vector store with HNSW indexing.
        
        Args:
            collection_name: Name of the collection to use
            persist_directory: Directory to store the database
            embedding_function: Function to use for embedding documents
            distance_function: Distance function for similarity search (cosine, l2, ip)
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.distance_function = distance_function
        
        # Ensure the persist directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB with HNSW indexing parameters
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                # HNSW index parameters for better recall/performance tradeoff
                chroma_hnsw_space=self.distance_function,  # Use cosine similarity
                chroma_hnsw_construction_ef=100,  # Higher values increase build time but improve index quality
                chroma_hnsw_search_ef=100,  # Higher values increase query time but improve recall
                chroma_hnsw_M=16  # Number of bidirectional links created for each new element
            )
        )
        
        # Set default embedding function if none is provided
        self.embedding_function = embedding_function or embedding_functions.DefaultEmbeddingFunction()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw_index": True, "distance_function": self.distance_function}
        )
    
    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None, ids: Optional[List[str]] = None):
        """Add documents to the vector store with automatic embeddings"""
        if not ids:
            # Generate UUIDs if no IDs provided
            import uuid
            ids = [str(uuid.uuid4()) for _ in range(len(documents))]
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        return ids
    
    def query(
        self, 
        query_text: str, 
        n_results: int = 5, 
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector store using semantic search with cosine similarity
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where
        )
        return results
    
    def delete(self, ids: Optional[List[str]] = None, where: Optional[Dict[str, Any]] = None):
        """Delete documents from the collection"""
        self.collection.delete(ids=ids, where=where)
    
    def rebuild_index(self):
        """
        Forces rebuilding of the HNSW index - useful after adding many documents
        """
        # ChromaDB automatically handles index updates, but we can reset the client
        # to force a complete rebuild when needed
        self.client.reset()
        # Reinitialize the collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw_index": True, "distance_function": self.distance_function}
        )
        return True
