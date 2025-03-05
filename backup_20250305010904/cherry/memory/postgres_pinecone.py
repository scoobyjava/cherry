import os
import uuid
import psycopg2
import pinecone
from datetime import datetime
from typing import List, Dict, Any, Optional

class PostgresPineconeMemory:
    """
    Memory storage implementation using PostgreSQL for metadata and Pinecone for vector embeddings.
    """
    
    def __init__(self, 
                 postgres_connection_string: str,
                 pinecone_api_key: str,
                 pinecone_environment: str,
                 pinecone_index_name: str,
                 embedding_dimension: int = 1536):
        """
        Initialize PostgreSQL and Pinecone connections.
        
        Args:
            postgres_connection_string: Connection string for PostgreSQL
            pinecone_api_key: API key for Pinecone
            pinecone_environment: Pinecone environment
            pinecone_index_name: Name of the Pinecone index
            embedding_dimension: Dimension of the embeddings
        """
        # PostgreSQL setup
        self.conn = psycopg2.connect(postgres_connection_string)
        self.create_tables()
        
        # Pinecone setup
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
        
        # Check if index exists, create if not
        if pinecone_index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=pinecone_index_name, 
                dimension=embedding_dimension,
                metric="cosine"
            )
        
        self.index = pinecone.Index(pinecone_index_name)
    
    def create_tables(self):
        """Create necessary tables in PostgreSQL if they don't exist."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id UUID PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMP NOT NULL
                );
            """)
            self.conn.commit()
    
    def store_memory(self, content: str, embedding: List[float], metadata: Dict[str, Any] = None) -> str:
        """
        Store a memory in PostgreSQL and its embedding in Pinecone.
        
        Args:
            content: Text content of the memory
            embedding: Vector embedding of the content
            metadata: Additional metadata for the memory
        
        Returns:
            The UUID of the stored memory
        """
        memory_id = str(uuid.uuid4())
        
        # Store in PostgreSQL
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO memories (id, content, metadata, created_at)
                VALUES (%s, %s, %s, %s)
                """,
                (memory_id, content, metadata or {}, datetime.now())
            )
            self.conn.commit()
        
        # Store in Pinecone
        self.index.upsert(
            vectors=[
                {
                    "id": memory_id,
                    "values": embedding,
                    "metadata": {"content": content[:100], **(metadata or {})}
                }
            ]
        )
        
        return memory_id
    
    def retrieve_memories(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve memories similar to the query embedding.
        
        Args:
            query_embedding: Vector embedding for the query
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of memories with their content and metadata
        """
        # Query Pinecone for similar vectors
        query_results = self.index.query(
            vector=query_embedding,
            top_k=limit,
            include_metadata=True
        )
        
        results = []
        
        # Get full data from PostgreSQL
        with self.conn.cursor() as cursor:
            for match in query_results['matches']:
                memory_id = match['id']
                cursor.execute(
                    "SELECT content, metadata, created_at FROM memories WHERE id = %s",
                    (memory_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    content, metadata, created_at = row
                    results.append({
                        "id": memory_id,
                        "content": content,
                        "metadata": metadata,
                        "created_at": created_at,
                        "score": match['score']
                    })
        
        return results
    
    def close(self):
        """Close database connections."""
        self.conn.close()
