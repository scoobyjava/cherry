import json
import logging
import os
import time
from datetime import datetime, timedelta

import pinecone
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

class PineconeArchiver:
    def __init__(self, config_path="/workspaces/cherry/benchmarks/benchmark_config.json", 
                 archival_config_path="/workspaces/cherry/archival/archival_config.json"):
        # Load configurations
        with open(config_path) as f:
            self.main_config = json.load(f)
        
        with open(archival_config_path) as f:
            self.archival_config = json.load(f)
        
        # Configure logging
        log_config = self.archival_config["archival"]["logging"]
        logging.basicConfig(
            filename=log_config["file_path"],
            level=getattr(logging, log_config["level"]),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("pinecone_archiver")
        
        # Initialize connections
        self._init_pinecone()
        self._init_postgres()

    def _init_pinecone(self):
        """Initialize Pinecone connection"""
        pinecone_config = self.main_config["pinecone"]
        api_key = self._resolve_secret(pinecone_config["api_key"])
        
        pinecone.init(
            api_key=api_key,
            environment=pinecone_config["environment"]
        )
        self.index = pinecone.Index(pinecone_config["index_name"])
        self.logger.info(f"Connected to Pinecone index: {pinecone_config['index_name']}")

    def _init_postgres(self):
        """Initialize PostgreSQL connection"""
        pg_config = self.main_config["postgres"]
        self.conn = psycopg2.connect(
            host=self._resolve_secret(pg_config["host"]),
            port=pg_config["port"],
            dbname=self._resolve_secret(pg_config["database"]),
            user=self._resolve_secret(pg_config["user"]),
            password=self._resolve_secret(pg_config["password"])
        )
        self.logger.info("Connected to PostgreSQL database")
        
        # Create tables if they don't exist
        self._ensure_tables_exist()

    def _resolve_secret(self, secret_string):
        """Resolve secret from environment or secret store"""
        if secret_string.startswith("${SECRET:") and secret_string.endswith("}"):
            # Extract the secret name and optional source
            parts = secret_string[9:-1].split(":", 1)
            secret_name = parts[0]
            
            # For simplicity, we're just using environment variables
            return os.environ.get(secret_name, "")
        return secret_string

    def _ensure_tables_exist(self):
        """Ensure the necessary tables exist in PostgreSQL"""
        tables = self.archival_config["tables"]["archived_vectors"]
        
        with self.conn.cursor() as cursor:
            for namespace, table_name in tables.items():
                # Get metadata schema for this namespace
                metadata_schema = self.main_config["pinecone"]["namespaces"][namespace]["metadata_schema"]
                
                # Build the SQL statement to create the table
                metadata_columns = []
                for field_name, field_type in metadata_schema.items():
                    pg_type = "TEXT" if field_type == "string" else "NUMERIC" if field_type == "number" else "TEXT"
                    metadata_columns.append(f"{field_name} {pg_type}")
                
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    vector_id TEXT NOT NULL,
                    namespace TEXT NOT NULL,
                    vector FLOAT[] NOT NULL,
                    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    {', '.join(metadata_columns)}
                );
                CREATE INDEX IF NOT EXISTS idx_{table_name}_vector_id ON {table_name} (vector_id);
                """
                
                cursor.execute(create_table_sql)
            
            self.conn.commit()
            self.logger.info("Ensured all archive tables exist")

    def archive_old_vectors(self):
        """Archive vectors older than the threshold from Pinecone to PostgreSQL"""
        dry_run = self.archival_config["archival"]["dry_run"]
        batch_size = self.archival_config["archival"]["batch_size"]
        age_threshold_days = self.archival_config["archival"]["age_threshold_days"]
        namespaces = self.archival_config["archival"]["namespaces_to_archive"]
        
        threshold_epoch = int((datetime.now() - timedelta(days=age_threshold_days)).timestamp())
        
        for namespace in namespaces:
            table_name = self.archival_config["tables"]["archived_vectors"][namespace]
            self.logger.info(f"Starting archival for namespace: {namespace}")
            
            # Get vectors older than threshold
            # Note: This assumes 'timestamp' field exists in metadata
            query_filter = {"timestamp": {"$lt": threshold_epoch}}
            
            total_archived = 0
            total_to_archive = 0
            
            # First, count the total vectors to archive
            try:
                stats = self.index.describe_index_stats(filter=query_filter, namespace=namespace)
                total_to_archive = stats.get("namespaces", {}).get(namespace, {}).get("vector_count", 0)
                self.logger.info(f"Found {total_to_archive} vectors to archive in namespace {namespace}")
            except Exception as e:
                self.logger.error(f"Error getting vector count: {str(e)}")
                continue

            if total_to_archive == 0:
                self.logger.info(f"No vectors to archive in namespace {namespace}")
                continue
                
            # Use pagination to process in batches
            next_pagination_token = None
            
            while True:
                try:
                    # Fetch vectors to archive
                    fetch_response = self.index.query(
                        vector=[0]*1536,  # Dummy vector for metadata-only query
                        filter=query_filter,
                        namespace=namespace,
                        top_k=batch_size,
                        include_values=True,
                        include_metadata=True,
                        pagination_token=next_pagination_token
                    )
                    
                    matches = fetch_response.get("matches", [])
                    if not matches:
                        break
                    
                    # Store in PostgreSQL
                    if not dry_run:
                        self._store_vectors_in_postgres(matches, namespace, table_name)
                    
                    # Delete from Pinecone
                    vector_ids = [match["id"] for match in matches]
                    if not dry_run:
                        self.index.delete(ids=vector_ids, namespace=namespace)
                    
                    total_archived += len(vector_ids)
                    self.logger.info(f"Archived batch of {len(vector_ids)} vectors. Total: {total_archived}/{total_to_archive}")
                    
                    # Check if we need to continue pagination
                    next_pagination_token = fetch_response.get("pagination_token")
                    if not next_pagination_token:
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error during archival: {str(e)}")
                    break
            
            self.logger.info(f"Completed archival for namespace {namespace}. Archived {total_archived} vectors.")

    def _store_vectors_in_postgres(self, matches, namespace, table_name):
        """Store vectors and metadata in PostgreSQL"""
        metadata_schema = self.main_config["pinecone"]["namespaces"][namespace]["metadata_schema"]
        
        with self.conn.cursor() as cursor:
            for match in matches:
                vector_id = match["id"]
                vector_values = match["values"]
                metadata = match.get("metadata", {})
                
                # Build columns and values for SQL
                columns = ["vector_id", "namespace", "vector"]
                values = [vector_id, namespace, vector_values]
                
                # Add metadata fields
                for field, _ in metadata_schema.items():
                    if field in metadata:
                        columns.append(field)
                        values.append(metadata[field])
                
                # Create the SQL query
                placeholders = ["%s"] * len(values)
                insert_sql = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                """
                
                cursor.execute(insert_sql, values)
            
            self.conn.commit()

    def close(self):
        """Close connections"""
        if hasattr(self, 'conn'):
            self.conn.close()
        self.logger.info("Connections closed")


if __name__ == "__main__":
    archiver = PineconeArchiver()
    try:
        archiver.archive_old_vectors()
    finally:
        archiver.close()
