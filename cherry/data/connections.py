import logging
import pinecone
import psycopg2
from psycopg2.extras import execute_values
from typing import Dict, List, Any, Optional, Tuple
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class PineconeClient:
    """Helper class for Pinecone operations."""
    
    def __init__(self, api_key: str, environment: str, index_name: str):
        """Initialize Pinecone connection."""
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.index = None
        
    def connect(self) -> None:
        """Establish connection to Pinecone."""
        try:
            pinecone.init(api_key=self.api_key, environment=self.environment)
            self.index = pinecone.Index(self.index_name)
            logger.info(f"Successfully connected to Pinecone index: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to connect to Pinecone: {str(e)}")
            raise
            
    def query_vectors_older_than(self, months: int = 6, limit: int = 1000) -> List[Dict[str, Any]]:
        """Query vectors that are older than the specified number of months."""
        if not self.index:
            self.connect()
        
        cutoff_date = datetime.now().replace(day=1)
        cutoff_date = cutoff_date.replace(month=cutoff_date.month - months if cutoff_date.month > months else cutoff_date.month + 12 - months, year=cutoff_date.year - (1 if cutoff_date.month <= months else 0))
        timestamp_threshold = int(cutoff_date.timestamp())
        
        # Note: This is a simplified approach. Actual implementation will depend on how you store timestamps in Pinecone.
        # Assuming you have a 'timestamp' metadata field in your vectors
        query_response = self.index.query(
            vector=[0] * 1536,  # Placeholder vector, actual implementation should use appropriate dimensionality
            top_k=limit,
            filter={"timestamp": {"$lt": timestamp_threshold}},
            include_metadata=True
        )
        
        return query_response.matches
    
    def delete_vectors(self, vector_ids: List[str]) -> bool:
        """Delete vectors from Pinecone by their IDs."""
        if not self.index:
            self.connect()
            
        try:
            self.index.delete(ids=vector_ids)
            logger.info(f"Deleted {len(vector_ids)} vectors from Pinecone")
            return True
        except Exception as e:
            logger.error(f"Failed to delete vectors from Pinecone: {str(e)}")
            return False
            

class PostgresClient:
    """Helper class for PostgreSQL operations."""
    
    def __init__(self, host: str, port: int, dbname: str, user: str, password: str):
        """Initialize PostgreSQL connection parameters."""
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.conn = None
        
    def connect(self) -> None:
        """Establish connection to PostgreSQL."""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
            logger.info(f"Successfully connected to PostgreSQL database: {self.dbname}")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
            raise
    
    def close(self) -> None:
        """Close the PostgreSQL connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            
    def __enter__(self):
        if not self.conn:
            self.connect()
        return self
            
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
            
    def store_vectors(self, vectors: List[Dict[str, Any]]) -> bool:
        """Store vectors in PostgreSQL archive table."""
        if not self.conn:
            self.connect()
            
        try:
            cursor = self.conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS archived_vectors (
                    id TEXT PRIMARY KEY,
                    vector FLOAT[] NOT NULL,
                    metadata JSONB,
                    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Prepare data for insertion
            vector_data = []
            for vec in vectors:
                vector_id = vec['id']
                vector_values = vec['values'] if 'values' in vec else []
                metadata = vec['metadata'] if 'metadata' in vec else {}
                vector_data.append((vector_id, vector_values, metadata))
                
            # Insert data using execute_values for efficiency
            execute_values(
                cursor,
                "INSERT INTO archived_vectors (id, vector, metadata) VALUES %s ON CONFLICT (id) DO NOTHING",
                vector_data,
                template="(%s, %s, %s::jsonb)"
            )
            
            self.conn.commit()
            cursor.close()
            
            logger.info(f"Stored {len(vectors)} vectors in PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"Failed to store vectors in PostgreSQL: {str(e)}")
            self.conn.rollback()
            return False
