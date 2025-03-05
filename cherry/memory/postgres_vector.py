import os
import json
import logging
import numpy as np
import psycopg2
from psycopg2.extras import execute_values, Json
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def get_postgres_connection():
    """Get a connection to the PostgreSQL database."""
    try:
        # Get database connection details from environment variables
        db_host = os.environ.get("POSTGRES_HOST", "localhost")
        db_port = os.environ.get("POSTGRES_PORT", "5432") 
        db_name = os.environ.get("POSTGRES_DB", "vector_db")
        db_user = os.environ.get("POSTGRES_USER", "postgres")
        db_password = os.environ.get("POSTGRES_PASSWORD", "")
        
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise

def init_postgres_vector_store(embedding_dimension: int = 1536) -> bool:
    """
    Initialize PostgreSQL with pgvector extension and create necessary tables.
    
    Args:
        embedding_dimension: Dimension of the embedding vectors
        
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    try:
        conn = get_postgres_connection()
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Enable pgvector extension
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create documents table
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS documents (
            document_id VARCHAR(255) PRIMARY KEY,
            document_text TEXT NOT NULL,
            metadata JSONB,
            agent_id VARCHAR(255),
            embedding vector({embedding_dimension}) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Create index for faster similarity searches
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS documents_embedding_idx 
        ON documents 
        USING ivfflat (embedding vector_cosine_ops) 
        WITH (lists = 100);
        """)
        
        # Create index on agent_id for faster filtering
        cursor.execute("CREATE INDEX IF NOT EXISTS documents_agent_id_idx ON documents(agent_id);")
        
        conn.close()
        logger.info("PostgreSQL vector store initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing PostgreSQL vector store: {e}")
        return False

def store_documents_in_postgres(documents: List[Dict[str, Any]], 
                               embedding_function, 
                               agent_id: Optional[str] = None) -> int:
    """
    Store documents in PostgreSQL with their embeddings.
    
    Args:
        documents: List of documents to store (with 'id', 'text', and optional 'metadata')
        embedding_function: Function that takes text and returns embeddings
        agent_id: Agent ID to associate with these documents
        
    Returns:
        int: Number of documents successfully stored
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Prepare data for batch insertion
        data_to_insert = []
        for doc in documents:
            doc_id = doc.get("id")
            doc_text = doc.get("text")
            metadata = Json(doc.get("metadata", {}))
            
            # Create embedding for the document text
            embedding = embedding_function(doc_text)
            
            data_to_insert.append((doc_id, doc_text, metadata, agent_id, embedding))
        
        # Batch insert into PostgreSQL
        insert_query = """
        INSERT INTO documents (document_id, document_text, metadata, agent_id, embedding)
        VALUES %s
        ON CONFLICT (document_id) DO UPDATE
        SET document_text = EXCLUDED.document_text,
            metadata = EXCLUDED.metadata,
            agent_id = EXCLUDED.agent_id,
            embedding = EXCLUDED.embedding
        """
        
        execute_values(cursor, insert_query, data_to_insert, template=None, page_size=100)
        conn.commit()
        conn.close()
        
        logger.info(f"Successfully stored {len(documents)} documents in PostgreSQL")
        return len(documents)
        
    except Exception as e:
        logger.error(f"Error storing documents in PostgreSQL: {e}")
        return 0

def fallback_retrieve_from_postgres(query_text: str, 
                                   embedding_function,
                                   top_n: int = 5, 
                                   agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fallback function to retrieve documents from PostgreSQL using pgvector similarity search
    when Pinecone is unavailable.
    
    Args:
        query_text: The text to search for semantically similar documents
        embedding_function: Function that converts text to embedding vector
        top_n: Number of results to return
        agent_id: Filter results by agent ID
    
    Returns:
        List of retrieved documents with similarity scores
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Get embedding for query text
        query_embedding = embedding_function(query_text)
        
        # Create query based on whether agent_id is provided
        if agent_id:
            query = """
                SELECT document_id, document_text, metadata, 
                       1 - (embedding <=> %s) as similarity
                FROM documents
                WHERE agent_id = %s
                ORDER BY embedding <=> %s
                LIMIT %s
            """
            cursor.execute(query, (query_embedding, agent_id, query_embedding, top_n))
        else:
            query = """
                SELECT document_id, document_text, metadata, 
                       1 - (embedding <=> %s) as similarity
                FROM documents
                ORDER BY embedding <=> %s
                LIMIT %s
            """
            cursor.execute(query, (query_embedding, query_embedding, top_n))
        
        results = []
        for row in cursor.fetchall():
            document_id, document_text, metadata, similarity = row
            results.append({
                "id": document_id,
                "text": document_text,
                "metadata": metadata,
                "score": float(similarity),
                "source": "postgres_fallback"
            })
        
        conn.close()
        logger.info(f"Retrieved {len(results)} documents from PostgreSQL fallback")
        return results
        
    except Exception as e:
        logger.error(f"Error retrieving from PostgreSQL: {e}")
        return []
