import psycopg2
import pinecone
import datetime
import logging
from typing import Dict, Any, Optional, Callable, List, Union

logger = logging.getLogger(__name__)

class MemoryStorageError(Exception):
    """Exception raised for errors in the memory storage process."""
    pass

def generate_embedding(content: str) -> List[float]:
    """
    Placeholder for the embedding generation function.
    In a real implementation, this would call a model to generate embeddings.
    
    Args:
        content: The text content to generate an embedding for
        
    Returns:
        List of floats representing the embedding vector
    """
    # This is a placeholder - implement with your actual embedding generation code
    raise NotImplementedError("This is a placeholder. Implement with actual embedding generation.")

def store_memory(
    content: str,
    metadata: Dict[str, Any],
    agent_id: str,
    embedding_func: Optional[Callable[[str], List[float]]] = None,
    pg_connection_string: str = "postgresql://username:password@localhost:5432/memory_db",
    pinecone_api_key: str = None,
    pinecone_environment: str = None,
    pinecone_index_name: str = "memory-index"
) -> int:
    """
    Store a new memory in PostgreSQL and Pinecone with transactional guarantees.
    
    Args:
        content: The text content of the memory
        metadata: Additional metadata for the memory
        agent_id: ID of the agent storing the memory
        embedding_func: Function to generate embeddings (uses default if None)
        pg_connection_string: PostgreSQL connection string
        pinecone_api_key: API key for Pinecone
        pinecone_environment: Pinecone environment
        pinecone_index_name: Name of the Pinecone index
        
    Returns:
        The ID of the stored memory
        
    Raises:
        MemoryStorageError: If there's an error storing the memory
    """
    if embedding_func is None:
        embedding_func = generate_embedding
    
    conn = None
    memory_id = None
    
    try:
        # Step 1: Generate embedding
        embedding = embedding_func(content)
        
        # Step 2: Insert into PostgreSQL
        conn = psycopg2.connect(pg_connection_string)
        cursor = conn.cursor()
        
        # Start transaction
        timestamp = datetime.datetime.utcnow()
        
        # Insert memory into PostgreSQL
        cursor.execute(
            """
            INSERT INTO memories 
            (content, embedding, metadata, agent_id, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (content, embedding, metadata, agent_id, timestamp)
        )
        
        # Get the memory ID
        memory_id = cursor.fetchone()[0]
        
        # Step 3: Upsert into Pinecone
        if pinecone_api_key and pinecone_environment:
            pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
            index = pinecone.Index(pinecone_index_name)
            
            # Upsert the vector into Pinecone using the PostgreSQL ID as the vector ID
            index.upsert(
                vectors=[{
                    "id": str(memory_id),
                    "values": embedding,
                    "metadata": {
                        **metadata,
                        "agent_id": agent_id,
                        "timestamp": timestamp.isoformat(),
                        "content": content
                    }
                }]
            )
        else:
            logger.warning("Pinecone credentials not provided. Skipping vector store upsert.")
        
        # Commit the transaction if everything succeeded
        conn.commit()
        logger.info(f"Successfully stored memory with ID {memory_id}")
        
        return memory_id
        
    except Exception as e:
        # Roll back the transaction if there was any error
        if conn:
            conn.rollback()
        
        logger.error(f"Error storing memory: {str(e)}")
        raise MemoryStorageError(f"Failed to store memory: {str(e)}")
        
    finally:
        # Close the database connection
        if conn:
            conn.close()
