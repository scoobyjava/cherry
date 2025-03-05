#!/usr/bin/env python3

import os
import sys
import time
import logging
import schedule
import json
import datetime
from typing import Dict, List, Optional, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_loader import load_config
from services.pg_service import PostgresService
from services.pinecone_service import PineconeService
from services.embedding_service import EmbeddingService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sync_pg_to_pinecone.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sync_pg_to_pinecone")

class MemorySyncService:
    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        
        # Initialize services
        self.pg_service = PostgresService(self.config["postgres"])
        self.pinecone_service = PineconeService(self.config["pinecone"])
        self.embedding_service = EmbeddingService(self.config["openai"])
        
        # Track namespaces from config
        self.namespaces = self.config["pinecone"]["namespaces"]
        
    def sync_embeddings(self):
        """Main method to synchronize PostgreSQL memory entries with Pinecone embeddings"""
        try:
            logger.info("Starting sync process...")
            
            # Get all namespaces to process
            for namespace, ns_config in self.namespaces.items():
                self._process_namespace(namespace, ns_config)
                
            logger.info("Sync process completed successfully")
        except Exception as e:
            logger.error(f"Error during sync process: {str(e)}", exc_info=True)
    
    def _process_namespace(self, namespace: str, ns_config: Dict[str, Any]):
        """Process a single namespace's worth of memory entries"""
        logger.info(f"Processing namespace: {namespace}")
        
        # Get memory entries from PostgreSQL for this namespace
        memory_entries = self._get_memory_entries(namespace)
        logger.info(f"Found {len(memory_entries)} entries in PostgreSQL for namespace {namespace}")
        
        if not memory_entries:
            logger.info(f"No entries to process for namespace {namespace}")
            return
            
        # Get existing vector IDs from Pinecone for this namespace
        existing_vectors = self.pinecone_service.list_vectors(namespace)
        logger.info(f"Found {len(existing_vectors)} existing vectors in Pinecone for namespace {namespace}")
        
        # Find entries that need embeddings
        entries_to_embed = []
        for entry in memory_entries:
            if str(entry["id"]) not in existing_vectors:
                entries_to_embed.append(entry)
                
        logger.info(f"{len(entries_to_embed)} entries need embeddings in namespace {namespace}")
        
        # Generate embeddings in batches
        batch_size = 10  # Adjust based on API limits and performance
        batches = [entries_to_embed[i:i+batch_size] for i in range(0, len(entries_to_embed), batch_size)]
        
        for batch_num, batch in enumerate(batches):
            logger.info(f"Processing batch {batch_num+1}/{len(batches)} for namespace {namespace}")
            
            # Generate embeddings
            embedding_inputs = [entry["content"] for entry in batch]
            embeddings = self.embedding_service.generate_embeddings(embedding_inputs)
            
            # Prepare vectors for upserting
            vectors_to_upsert = []
            for i, entry in enumerate(batch):
                # Create metadata based on namespace schema
                metadata = self._create_metadata_for_namespace(namespace, entry)
                
                vectors_to_upsert.append({
                    "id": str(entry["id"]),
                    "values": embeddings[i],
                    "metadata": metadata
                })
            
            # Upsert to Pinecone
            if vectors_to_upsert:
                self.pinecone_service.upsert_vectors(namespace, vectors_to_upsert)
                logger.info(f"Upserted {len(vectors_to_upsert)} vectors to namespace {namespace}")
            
            # Avoid rate limiting
            if batch_num < len(batches) - 1:
                time.sleep(1)
                
        logger.info(f"Completed processing for namespace {namespace}")
    
    def _get_memory_entries(self, namespace: str) -> List[Dict[str, Any]]:
        """Query PostgreSQL for memory entries related to the given namespace"""
        # This is a simplified example - adjust the query based on your schema
        query = f"""
            SELECT id, content, created_at, updated_at, metadata 
            FROM memory_entries 
            WHERE namespace = %s AND (
                updated_at > NOW() - INTERVAL '24 hours'
                OR id NOT IN (SELECT entry_id FROM embedded_entries)
            )
        """
        
        results = self.pg_service.execute_query(query, (namespace,))
        return results
    
    def _create_metadata_for_namespace(self, namespace: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Create metadata for Pinecone based on the namespace schema and entry data"""
        schema = self.namespaces[namespace]["metadata_schema"]
        metadata = {}
        
        # Extract metadata from the entry based on schema
        entry_metadata = entry.get("metadata", {})
        
        for field, field_type in schema.items():
            if field in entry_metadata:
                # Convert to appropriate type based on schema
                if field_type == "number" and isinstance(entry_metadata[field], (int, float)):
                    metadata[field] = float(entry_metadata[field])
                elif field_type == "string" and isinstance(entry_metadata[field], str):
                    metadata[field] = entry_metadata[field]
        
        # Add timestamp if not present
        if "timestamp" in schema and "timestamp" not in metadata:
            metadata["timestamp"] = datetime.datetime.now().timestamp()
            
        return metadata

def run_sync_job():
    """Function to run the sync job"""
    logger.info("Starting scheduled sync job")
    sync_service = MemorySyncService("/workspaces/cherry/benchmarks/benchmark_config.json")
    sync_service.sync_embeddings()
    logger.info("Completed scheduled sync job")

if __name__ == "__main__":
    # Set up schedule - run every hour by default
    schedule.every().hour.do(run_sync_job)
    
    # Run immediately on startup
    run_sync_job()
    
    # Keep running according to schedule
    while True:
        schedule.run_pending()
        time.sleep(60)  # Sleep for 1 minute between checks
