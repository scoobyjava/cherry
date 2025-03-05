import os
import uuid
import time
from typing import Dict, List, Optional, Any, Tuple

import pinecone
from pinecone import Pinecone, ServerlessSpec

class PineconeMemory:
    """Memory system that stores and retrieves embeddings from Pinecone with agent namespaces."""
    
    def __init__(
        self,
        api_key: str = None,
        environment: str = None,
        index_name: str = "cherry-memory",
        dimension: int = 1536,  # Default for OpenAI embeddings
        metric: str = "cosine",
        server_side_timeout: int = 20,
        cloud: str = "aws",
        region: str = "us-west-2"
    ):
        """
        Initialize Pinecone memory system with namespace support.
        
        Args:
            api_key: Pinecone API key (defaults to PINECONE_API_KEY env var)
            environment: Pinecone environment (defaults to PINECONE_ENVIRONMENT env var)
            index_name: Name of the Pinecone index
            dimension: Dimension of embedding vectors
            metric: Distance metric for similarity search
            server_side_timeout: Server-side timeout in seconds
            cloud: Cloud provider (aws, gcp, azure)
            region: Cloud region
        """
        self.api_key = api_key or os.environ.get("PINECONE_API_KEY")
        self.environment = environment or os.environ.get("PINECONE_ENVIRONMENT")
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        self.timeout = server_side_timeout
        self.cloud = cloud
        self.region = region
        
        if not self.api_key:
            raise ValueError("Pinecone API key not provided and PINECONE_API_KEY not found in environment")
        
        # Initialize the Pinecone client
        self.pc = Pinecone(api_key=self.api_key)
        
        # Check if index exists, create if it doesn't
        self._initialize_index()
        
    def _initialize_index(self):
        """Initialize Pinecone index if it doesn't exist."""
        # List existing indexes
        existing_indexes = [index_info["name"] for index_info in self.pc.list_indexes()]
        
        # Create index if it doesn't exist
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(
                    cloud=self.cloud,
                    region=self.region
                )
            )
            print(f"Created new Pinecone index: {self.index_name}")
            # Wait for index to be ready
            time.sleep(1)
        
        # Connect to the index
        self.index = self.pc.Index(self.index_name)
    
    def upsert(
        self,
        vectors: List[List[float]],
        texts: List[str],
        metadata: List[Dict[str, Any]],
        agent_id: str,
        batch_size: int = 100
    ) -> List[str]:
        """
        Upsert vectors into Pinecone index with agent-specific namespace.
        
        Args:
            vectors: List of embedding vectors
            texts: List of corresponding text content
            metadata: List of metadata for each vector
            agent_id: Agent ID for namespace segmentation
            batch_size: Size of batches for upserting
        
        Returns:
            List of IDs for the upserted vectors
        """
        if not vectors or len(vectors) != len(texts) or len(vectors) != len(metadata):
            raise ValueError("Vectors, texts, and metadata must have the same length and not be empty")
            
        # Generate IDs if not provided in metadata
        ids = [meta.get("id", str(uuid.uuid4())) for meta in metadata]
        
        # Update metadata with text content
        for i, (text, meta) in enumerate(zip(texts, metadata)):
            metadata[i]["text"] = text
        
        # Prepare items for upsert
        items_to_upsert = []
        for i, (vector, meta, id_value) in enumerate(zip(vectors, metadata, ids)):
            items_to_upsert.append({
                "id": id_value,
                "values": vector,
                "metadata": meta
            })
        
        # Upsert vectors in batches
        for i in range(0, len(items_to_upsert), batch_size):
            batch = items_to_upsert[i:i + batch_size]
            self.index.upsert(vectors=batch, namespace=agent_id)
            
        return ids
    
    def query(
        self,
        query_vector: List[float],
        agent_id: str,
        top_k: int = 5,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Query similar vectors from a specific agent's namespace.
        
        Args:
            query_vector: The embedding vector to search with
            agent_id: Agent ID to search within
            top_k: Number of results to return
            include_metadata: Whether to include metadata in results
        
        Returns:
            List of similar items with scores and metadata
        """
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            namespace=agent_id,
            include_metadata=include_metadata
        )
        
        return results.get("matches", [])
    
    def delete(self, ids: List[str], agent_id: str):
        """
        Delete vectors by ID from a specific agent's namespace.
        
        Args:
            ids: List of vector IDs to delete
            agent_id: Agent ID namespace
        """
        self.index.delete(ids=ids, namespace=agent_id)
    
    def list_namespaces(self) -> List[str]:
        """
        Get list of all namespaces (agent IDs) in the index.
        
        Returns:
            List of namespace names
        """
        stats = self.index.describe_index_stats()
        return list(stats.get("namespaces", {}).keys())
    
    def get_namespace_stats(self, agent_id: str = None) -> Dict:
        """
        Get statistics for a specific namespace or all namespaces.
        
        Args:
            agent_id: Optional agent ID to get stats for
        
        Returns:
            Dictionary of namespace statistics
        """
        stats = self.index.describe_index_stats()
        if agent_id:
            return stats.get("namespaces", {}).get(agent_id, {})
        return stats.get("namespaces", {})
