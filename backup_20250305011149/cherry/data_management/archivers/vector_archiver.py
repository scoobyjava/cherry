"""
Vector archiver for moving old vectors from Pinecone to PostgreSQL.
"""
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from cherry.data_management.connectors.pinecone_connector import PineconeConnector
from cherry.data_management.connectors.postgres_connector import PostgresConnector
from logger import get_logger

logger = get_logger(__name__)

class VectorArchiver:
    """
    Vector archiver for moving old vectors from Pinecone to PostgreSQL.
    Implements an automated routine to archive or delete vectors in Pinecone
    that are older than 6 months to control costs, while ensuring long-term
    data remains stored in PostgreSQL.
    """
    
    def __init__(
        self,
        pinecone_index: str,
        archive_age_months: int = 6,
        delete_after_archive: bool = True,
        archive_table: str = "archived_vectors",
        batch_size: int = 100
    ):
        """
        Initialize Vector Archiver.
        
        Args:
            pinecone_index: Name of the Pinecone index to archive from.
            archive_age_months: Archive vectors older than this many months.
            delete_after_archive: Whether to delete vectors from Pinecone after archiving.
            archive_table: Name of the PostgreSQL table for archived vectors.
            batch_size: Number of vectors to process in a single batch.
        """
        self.pinecone_index = pinecone_index
        self.archive_age_months = archive_age_months
        self.delete_after_archive = delete_after_archive
        self.archive_table = archive_table
        self.batch_size = batch_size
        
        self.pinecone = PineconeConnector()
        self.postgres = PostgresConnector()
        
    def run_archival(self) -> Dict[str, Any]:
        """
        Run the archival process.
        
        Returns:
            Dictionary with archival statistics.
        """
        start_time = time.time()
        logger.info(f"Starting archival process for vectors older than {self.archive_age_months} months")
        
        stats = {
            "found_vectors": 0,
            "archived_vectors": 0,
            "deleted_vectors": 0,
            "errors": 0,
            "start_time": datetime.now().isoformat(),
            "elapsed_seconds": 0
        }
        
        try:
            # Step 1: Find old vectors
            old_vector_ids = self.pinecone.find_vectors_older_than(
                self.pinecone_index, 
                months=self.archive_age_months
            )
            stats["found_vectors"] = len(old_vector_ids)
            
            if not old_vector_ids:
                logger.info("No vectors found that need archiving")
                stats["elapsed_seconds"] = time.time() - start_time
                return stats
                
            # Step 2: Process vectors in batches
            for i in range(0, len(old_vector_ids), self.batch_size):
                batch_ids = old_vector_ids[i:i+self.batch_size]
                
                # Fetch vector data from Pinecone
                vector_data = self.pinecone.fetch_vectors_by_ids(self.pinecone_index, batch_ids)
                
                # Archive to PostgreSQL
                try:
                    archived_count = self.postgres.archive_vectors(
                        vector_data, 
                        self.pinecone_index, 
                        self.archive_table
                    )
                    stats["archived_vectors"] += archived_count
                    
                    # Delete from Pinecone if configured
                    if self.delete_after_archive:
                        if self.pinecone.delete_vectors(self.pinecone_index, batch_ids):
                            stats["deleted_vectors"] += len(batch_ids)
                        
                except Exception as e:
                    logger.error(f"Error archiving batch: {e}")
                    stats["errors"] += 1
                    
                # Small delay to avoid overwhelming the APIs
                time.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Error during archival process: {e}")
            stats["errors"] += 1
            
        finally:
            # Ensure database connections are closed
            self.postgres.disconnect()
            
            # Calculate elapsed time
            stats["elapsed_seconds"] = time.time() - start_time
            stats["end_time"] = datetime.now().isoformat()
            
            logger.info(f"Archival process completed in {stats['elapsed_seconds']:.2f} seconds")
            logger.info(f"Found: {stats['found_vectors']}, Archived: {stats['archived_vectors']}, "
                       f"Deleted: {stats['deleted_vectors']}, Errors: {stats['errors']}")
            
            return stats

def archive_old_vectors(index_name: str, months: int = 6) -> Dict[str, Any]:
    """
    Utility function to archive old vectors.
    
    Args:
        index_name: Name of the Pinecone index.
        months: Archive vectors older than this many months.
        
    Returns:
        Dictionary with archival statistics.
    """
    archiver = VectorArchiver(index_name, archive_age_months=months)
    return archiver.run_archival()
