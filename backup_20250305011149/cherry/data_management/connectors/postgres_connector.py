"""
Connector for PostgreSQL database.
"""
import os
import json
from typing import Dict, List, Optional, Any, Tuple

import psycopg2
from psycopg2.extras import Json

from logger import get_logger

logger = get_logger(__name__)

class PostgresConnector:
    """Connector for PostgreSQL database."""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize PostgreSQL connector.
        
        Args:
            host: Database host. If None, will try to get from environment variables.
            port: Database port. If None, will try to get from environment variables.
            database: Database name. If None, will try to get from environment variables.
            user: Database user. If None, will try to get from environment variables.
            password: Database password. If None, will try to get from environment variables.
        """
        self.host = host or os.environ.get("POSTGRES_HOST", "localhost")
        self.port = port or int(os.environ.get("POSTGRES_PORT", "5432"))
        self.database = database or os.environ.get("POSTGRES_DB", "cherry")
        self.user = user or os.environ.get("POSTGRES_USER", "postgres")
        self.password = password or os.environ.get("POSTGRES_PASSWORD", "")
        
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Connect to PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor()
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            raise
            
    def disconnect(self):
        """Disconnect from PostgreSQL database."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            logger.info("Disconnected from PostgreSQL database")
        except Exception as e:
            logger.error(f"Error disconnecting from PostgreSQL: {e}")
            
    def ensure_vector_archive_table(self, table_name: str = "archived_vectors"):
        """
        Ensure the vector archive table exists.
        
        Args:
            table_name: Name of the archive table.
        """
        if not self.connection:
            self.connect()
            
        try:
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id VARCHAR(255) PRIMARY KEY,
                    vector REAL[],
                    metadata JSONB,
                    source_index VARCHAR(255),
                    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.connection.commit()
            logger.info(f"Vector archive table '{table_name}' is ready")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error creating vector archive table: {e}")
            raise
    
    def archive_vectors(self, vectors: Dict[str, Any], source_index: str, table_name: str = "archived_vectors") -> int:
        """
        Archive vectors to PostgreSQL.
        
        Args:
            vectors: Dictionary of vectors with their metadata.
            source_index: Name of the source Pinecone index.
            table_name: Name of the archive table.
            
        Returns:
            Number of vectors archived.
        """
        if not self.connection:
            self.connect()
            
        self.ensure_vector_archive_table(table_name)
        
        count = 0
        try:
            for vector_id, vector_data in vectors.items():
                # Extract values and metadata
                values = vector_data.get('values', [])
                metadata = vector_data.get('metadata', {})
                
                # Insert into PostgreSQL
                self.cursor.execute(
                    f"""
                    INSERT INTO {table_name} (id, vector, metadata, source_index)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                    SET vector = EXCLUDED.vector,
                        metadata = EXCLUDED.metadata,
                        source_index = EXCLUDED.source_index,
                        archived_at = CURRENT_TIMESTAMP
                    """,
                    (vector_id, values, Json(metadata), source_index)
                )
                count += 1
                
            self.connection.commit()
            logger.info(f"Successfully archived {count} vectors to PostgreSQL")
            return count
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error archiving vectors to PostgreSQL: {e}")
            raise
            
    def get_archived_vectors(self, source_index: Optional[str] = None, table_name: str = "archived_vectors") -> List[Dict]:
        """
        Get archived vectors from PostgreSQL.
        
        Args:
            source_index: Filter by source index. If None, get all vectors.
            table_name: Name of the archive table.
            
        Returns:
            List of archived vectors.
        """
        if not self.connection:
            self.connect()
            
        try:
            if source_index:
                self.cursor.execute(
                    f"""
                    SELECT id, vector, metadata, source_index, archived_at
                    FROM {table_name}
                    WHERE source_index = %s
                    """,
                    (source_index,)
                )
            else:
                self.cursor.execute(
                    f"""
                    SELECT id, vector, metadata, source_index, archived_at
                    FROM {table_name}
                    """
                )
                
            rows = self.cursor.fetchall()
            results = []
            
            for row in rows:
                results.append({
                    "id": row[0],
                    "vector": row[1],
                    "metadata": row[2],
                    "source_index": row[3],
                    "archived_at": row[4]
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Error fetching archived vectors: {e}")
            raise
