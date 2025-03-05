import asyncio
import logging
from typing import Dict, List, Set, Tuple, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import pinecone
from pinecone import PineconeException
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("cherry.memory_verification")

class MemoryVerifier:
    def __init__(self):
        self.pg_conn_string = os.getenv("POSTGRES_CONNECTION_STRING", "")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY", "")
        self.pinecone_env = os.getenv("PINECONE_ENVIRONMENT", "")
        self.index_name = os.getenv("PINECONE_INDEX", "cherry-memories")
        self.namespace = "uiux_agent"  # Namespace for UIUXAgent memories
        
    async def initialize(self):
        """Initialize connections to PostgreSQL and Pinecone."""
        # Initialize Pinecone
        pinecone.init(api_key=self.pinecone_api_key, environment=self.pinecone_env)
        if self.index_name not in pinecone.list_indexes():
            logger.error(f"Pinecone index {self.index_name} not found")
            raise ValueError(f"Pinecone index {self.index_name} not found")
        
        # Test PostgreSQL connection
        try:
            with psycopg2.connect(self.pg_conn_string) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
            
        logger.info("Memory verifier initialized successfully")
        
    async def get_postgres_memories(self) -> Dict[str, Dict]:
        """Fetch all UIUXAgent memories from PostgreSQL."""
        memories = {}
        try:
            with psycopg2.connect(self.pg_conn_string) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT id, content, metadata, created_at, updated_at
                        FROM memories
                        WHERE agent_id = 'uiux_agent'
                        """
                    )
                    for row in cursor.fetchall():
                        memory_id = str(row['id'])
                        memories[memory_id] = dict(row)
            logger.info(f"Retrieved {len(memories)} memories from PostgreSQL")
            return memories
        except Exception as e:
            logger.error(f"Error fetching memories from PostgreSQL: {e}")
            raise
            
    async def get_pinecone_memories(self) -> Dict[str, Dict]:
        """Fetch all UIUXAgent memories from Pinecone."""
        memories = {}
        try:
            index = pinecone.Index(self.index_name)
            # We'll need to fetch in batches as Pinecone has limits
            # This is a simplified version - in production you might need pagination
            query_response = index.fetch(
                ids=[], 
                namespace=self.namespace
            )
            
            for memory_id, memory_data in query_response.get('vectors', {}).items():
                memories[memory_id] = {
                    'id': memory_id,
                    'metadata': memory_data.get('metadata', {}),
                    'vector': memory_data.get('values')
                }
            
            logger.info(f"Retrieved {len(memories)} memories from Pinecone")
            return memories
        except PineconeException as e:
            logger.error(f"Error fetching memories from Pinecone: {e}")
            raise
    
    async def verify_memories(self) -> Dict[str, Any]:
        """Verify that memories exist in both PostgreSQL and Pinecone."""
        pg_memories = await self.get_postgres_memories()
        pinecone_memories = await self.get_pinecone_memories()
        
        pg_ids = set(pg_memories.keys())
        pinecone_ids = set(pinecone_memories.keys())
        
        # Find discrepancies
        missing_in_pinecone = pg_ids - pinecone_ids
        missing_in_postgres = pinecone_ids - pg_ids
        
        result = {
            "verified_at": datetime.utcnow().isoformat(),
            "total_pg_memories": len(pg_memories),
            "total_pinecone_memories": len(pinecone_memories),
            "missing_in_pinecone": list(missing_in_pinecone),
            "missing_in_postgres": list(missing_in_postgres),
            "has_discrepancies": bool(missing_in_pinecone or missing_in_postgres)
        }
        
        logger.info(f"Memory verification complete: {result['has_discrepancies']=}")
        if result["has_discrepancies"]:
            logger.warning(f"Found discrepancies: {len(missing_in_pinecone)} missing in Pinecone, "
                          f"{len(missing_in_postgres)} missing in PostgreSQL")
        
        return result
    
    async def reconcile_memories(self) -> Dict[str, Any]:
        """Fix discrepancies between PostgreSQL and Pinecone memories."""
        verification = await self.verify_memories()
        
        reconciliation_results = {
            "reconciled_at": datetime.utcnow().isoformat(),
            "fixed_in_pinecone": 0,
            "fixed_in_postgres": 0,
            "failed_fixes": 0,
            "details": []
        }
        
        if not verification["has_discrepancies"]:
            logger.info("No discrepancies found, skipping reconciliation")
            return reconciliation_results
        
        # Get full memory data for reconciliation
        pg_memories = await self.get_postgres_memories()
        pinecone_memories = await self.get_pinecone_memories()
        
        # Fix missing memories in Pinecone
        # This is a placeholder - actual implementation would need to 
        # generate vectors for the PostgreSQL memories and upsert to Pinecone
        for memory_id in verification["missing_in_pinecone"]:
            try:
                if memory_id in pg_memories:
                    logger.info(f"Would restore memory {memory_id} to Pinecone")
                    # Actual implementation would involve:
                    # 1. Generating embedding for the memory content
                    # 2. Upserting to Pinecone
                    # index.upsert([(memory_id, vector, metadata)], namespace=self.namespace)
                    reconciliation_results["fixed_in_pinecone"] += 1
                    reconciliation_results["details"].append({
                        "memory_id": memory_id,
                        "action": "restore_to_pinecone",
                        "status": "simulated" # Would be "success" in real implementation
                    })
            except Exception as e:
                logger.error(f"Failed to restore memory {memory_id} to Pinecone: {e}")
                reconciliation_results["failed_fixes"] += 1
                reconciliation_results["details"].append({
                    "memory_id": memory_id,
                    "action": "restore_to_pinecone",
                    "status": "error",
                    "error": str(e)
                })
        
        # Fix missing memories in PostgreSQL
        # This is a placeholder - actual implementation would need to
        # reconstruct memory records from Pinecone data and insert to PostgreSQL
        for memory_id in verification["missing_in_postgres"]:
            try:
                if memory_id in pinecone_memories:
                    logger.info(f"Would restore memory {memory_id} to PostgreSQL")
                    # Actual implementation would involve:
                    # 1. Extracting metadata from Pinecone
                    # 2. Inserting to PostgreSQL
                    reconciliation_results["fixed_in_postgres"] += 1
                    reconciliation_results["details"].append({
                        "memory_id": memory_id,
                        "action": "restore_to_postgres",
                        "status": "simulated" # Would be "success" in real implementation
                    })
            except Exception as e:
                logger.error(f"Failed to restore memory {memory_id} to PostgreSQL: {e}")
                reconciliation_results["failed_fixes"] += 1
                reconciliation_results["details"].append({
                    "memory_id": memory_id,
                    "action": "restore_to_postgres",
                    "status": "error",
                    "error": str(e)
                })
        
        logger.info(f"Reconciliation complete: fixed {reconciliation_results['fixed_in_pinecone']} in Pinecone, "
                   f"{reconciliation_results['fixed_in_postgres']} in PostgreSQL, "
                   f"{reconciliation_results['failed_fixes']} failures")
        
        return reconciliation_results

async def verify_and_reconcile_memories():
    """Utility function to perform verification and reconciliation."""
    verifier = MemoryVerifier()
    await verifier.initialize()
    verification_result = await verifier.verify_memories()
    
    if verification_result["has_discrepancies"]:
        logger.warning("Discrepancies found, running reconciliation")
        reconciliation_result = await verifier.reconcile_memories()
        return {
            "verification": verification_result,
            "reconciliation": reconciliation_result
        }
    else:
        logger.info("No discrepancies found")
        return {
            "verification": verification_result,
            "reconciliation": None
        }
