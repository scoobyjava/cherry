import json
import time
from typing import Dict, List, Any, Optional

import pinecone
import psycopg2
from psycopg2.extras import Json

from .embeddings import generate_embedding

class MemoryStoreException(Exception):
    """Custom exception for memory store operations."""
    pass

def store_memory(
    content: str,
    metadata: Dict[str, Any],
    agent_id: str,
    namespace: str,
    timestamp: Optional[float] = None,
    config_path: str = "/workspaces/cherry/benchmarks/benchmark_config.json"
) -> str:
    """
    Store a new memory by generating an embedding, inserting into PostgreSQL,
    and upserting into Pinecone with transactional guarantees.
    
    Args:
        content: The text content to store
        metadata: Dictionary of metadata associated with the memory
        agent_id: Identifier for the agent associated with this memory
        namespace: The Pinecone namespace to use
        timestamp: Optional timestamp, defaults to current time if not provided
        config_path: Path to the configuration file
        
    Returns:
        The ID of the newly created memory
        
    Raises:
        MemoryStoreException: If any part of the storage process fails
    """
    timestamp = timestamp or time.time()
    conn = None
    
    try:
        # Load configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Generate embedding
        embedding = generate_embedding(content)
        if not embedding:
            raise MemoryStoreException("Failed to generate embedding for content")
        
        # Validate namespace exists in config
        pinecone_config = config.get('pinecone', {})
        namespaces_config = pinecone_config.get('namespaces', {})
        if namespace not in namespaces_config:
            raise MemoryStoreException(f"Namespace '{namespace}' not found in configuration")
        
        # Establish PostgreSQL connection
        pg_config = config.get('postgres', {})
        conn = psycopg2.connect(
            host=pg_config.get('host'),
            port=pg_config.get('port'),
            database=pg_config.get('database'),
            user=pg_config.get('user'),
            password=pg_config.get('password')
        )
        
        # Begin transaction
        conn.autocommit = False
        
        try:
            with conn.cursor() as cur:
                # Insert memory into PostgreSQL
                cur.execute(
                    """
                    INSERT INTO memories 
                    (content, embedding, metadata, agent_id, namespace, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (content, embedding, Json(metadata), agent_id, namespace, timestamp)
                )
                
                # Get the new memory ID
                memory_id = cur.fetchone()[0]
                
                # Initialize Pinecone
                pinecone.init(
                    api_key=pinecone_config.get('api_key'),
                    environment=pinecone_config.get('environment')
                )
                
                # Get the Pinecone index
                index_name = pinecone_config.get('index_name')
                index = pinecone.Index(index_name)
                
                # Upsert the embedding into Pinecone
                upsert_response = index.upsert(
                    vectors=[(str(memory_id), embedding, metadata)],
                    namespace=namespace
                )
                
                # Commit transaction only if Pinecone upsert succeeded
                conn.commit()
                
                return str(memory_id)
                
        except Exception as e:
            # Rollback on error
            if conn and not conn.closed:
                conn.rollback()
            raise MemoryStoreException(f"Failed to store memory: {str(e)}")
            
    except Exception as e:
        raise MemoryStoreException(f"Memory storage operation failed: {str(e)}")
    
    finally:
        # Always close the connection if it exists
        if conn and not conn.closed:
            conn.close()
