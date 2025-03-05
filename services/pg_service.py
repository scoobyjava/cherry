import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Tuple, Optional, Union

logger = logging.getLogger(__name__)

class PostgresService:
    def __init__(self, config: Dict[str, Any]):
        """Initialize PostgreSQL service with config"""
        self.config = config
        self._conn = None
        
        # Process environment variables or secrets in connection details
        self.host = self._process_config_value(config["host"])
        self.port = config["port"]
        self.database = self._process_config_value(config["database"])
        self.user = self._process_config_value(config["user"])
        self.password = self._process_config_value(config["password"])
    
    def _process_config_value(self, value: str) -> str:
        """Process configuration values that might contain references to secrets or env vars"""
        if value.startswith("${SECRET:") and value.endswith("}"):
            # Extract secret name and optional source
            parts = value[9:-1].split(":")
            secret_name = parts[0]
            
            # Check if source is specified (env_var or file)
            if len(parts) > 1 and parts[1] == "env_var":
                return os.environ.get(secret_name, "")
            else:
                # Default to environment variable
                return os.environ.get(secret_name, "")
        return value
    
    def get_connection(self):
        """Get or create a database connection"""
        if self._conn is None or self._conn.closed:
            try:
                self._conn = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    dbname=self.database,
                    user=self.user,
                    password=self.password
                )
                logger.info("Connected to PostgreSQL database")
            except Exception as e:
                logger.error(f"Error connecting to PostgreSQL: {str(e)}")
                raise
        return self._conn
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as a list of dictionaries"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                
                if cursor.description:  # If query returns rows
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                
                conn.commit()
                return []
        except Exception as e:
            conn.rollback()
            logger.error(f"Error executing query: {str(e)}")
            raise
    
    def execute_batch(self, query: str, params_list: List[Tuple]) -> None:
        """Execute a batch of queries with different parameters"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                for params in params_list:
                    cursor.execute(query, params)
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error executing batch query: {str(e)}")
            raise
    
    def close(self):
        """Close the database connection"""
        if self._conn and not self._conn.closed:
            self._conn.close()
            self._conn = None
