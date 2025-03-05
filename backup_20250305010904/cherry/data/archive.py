import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import schedule
import os

from cherry.data.connections import PineconeClient, PostgresClient

logger = logging.getLogger(__name__)

class VectorArchiver:
    """
    Handles archiving of old vectors from Pinecone to PostgreSQL.
    """
    
    def __init__(self, 
                 pinecone_api_key: str,
                 pinecone_env: str,
                 pinecone_index: str,
                 pg_host: str,
                 pg_port: int,
                 pg_dbname: str,
                 pg_user: str,
                 pg_password: str,
                 archive_age_months: int = 6,
                 batch_size: int = 100):
        """
        Initialize the vector archiver.
        
        Args:
            pinecone_api_key: Pinecone API key
            pinecone_env: Pinecone environment
            pinecone_index: Pinecone index name
            pg_host: PostgreSQL host
            pg_port: PostgreSQL port
            pg_dbname: PostgreSQL database name
            pg_user: PostgreSQL username
            pg_password: PostgreSQL password
            archive_age_months: Age in months after which vectors should be archived
            batch_size: Number of vectors to process in each batch
        """
        self.pinecone_client = PineconeClient(
            api_key=pinecone_api_key,
            environment=pinecone_env,
            index_name=pinecone_index
        )
        
        self.postgres_client = PostgresClient(
            host=pg_host,
            port=pg_port,
            dbname=pg_dbname,
            user=pg_user,
            password=pg_password
        )
        
        self.archive_age_months = archive_age_months
        self.batch_size = batch_size
        
    def run_archive_job(self) -> Tuple[int, int]:
        """
        Run the archiving job to move old vectors from Pinecone to PostgreSQL.
        
        Returns:
            Tuple containing count of vectors archived and count of vectors deleted
        """
        logger.info(f"Starting archiving job for vectors older than {self.archive_age_months} months")
        
        try:
            # Connect to both databases
            self.pinecone_client.connect()
            self.postgres_client.connect()
            
            # Get old vectors from Pinecone
            old_vectors = self.pinecone_client.query_vectors_older_than(
                months=self.archive_age_months, 
                limit=self.batch_size
            )
            
            if not old_vectors:
                logger.info("No vectors found to archive")
                return 0, 0
                
            logger.info(f"Found {len(old_vectors)} vectors to archive")
            
            # Store vectors in PostgreSQL
            success = self.postgres_client.store_vectors(old_vectors)
            if not success:
                logger.error("Failed to store vectors in PostgreSQL. Aborting deletion from Pinecone.")
                return 0, 0
                
            # Delete vectors from Pinecone
            vector_ids = [vec['id'] for vec in old_vectors]
            deleted = self.pinecone_client.delete_vectors(vector_ids)
            
            if deleted:
                logger.info(f"Successfully archived {len(vector_ids)} vectors from Pinecone to PostgreSQL")
                return len(old_vectors), len(vector_ids)
            else:
                logger.error("Failed to delete vectors from Pinecone")
                return len(old_vectors), 0
                
        except Exception as e:
            logger.exception(f"Error during archiving job: {str(e)}")
            return 0, 0
        finally:
            # Close PostgreSQL connection
            self.postgres_client.close()
            
    def schedule_regular_archiving(self, schedule_time: str = "02:00") -> None:
        """
        Schedule regular archiving to run at a specific time every day.
        
        Args:
            schedule_time: Time to run the job in 24-hour format (HH:MM)
        """
        logger.info(f"Scheduling archiving job to run at {schedule_time} daily")
        schedule.every().day.at(schedule_time).do(self.run_archive_job)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Sleep for a minute between checks


def run_archiver_from_config(config_dict: Dict[str, Any]) -> None:
    """
    Run the vector archiver using configuration from a dictionary.
    
    Args:
        config_dict: Dictionary containing configuration values
    """
    archiver = VectorArchiver(
        pinecone_api_key=config_dict.get("PINECONE_API_KEY", ""),
        pinecone_env=config_dict.get("PINECONE_ENVIRONMENT", ""),
        pinecone_index=config_dict.get("PINECONE_INDEX", ""),
        pg_host=config_dict.get("POSTGRES_HOST", "localhost"),
        pg_port=int(config_dict.get("POSTGRES_PORT", 5432)),
        pg_dbname=config_dict.get("POSTGRES_DB", ""),
        pg_user=config_dict.get("POSTGRES_USER", ""),
        pg_password=config_dict.get("POSTGRES_PASSWORD", ""),
        archive_age_months=int(config_dict.get("ARCHIVE_AGE_MONTHS", 6)),
        batch_size=int(config_dict.get("ARCHIVE_BATCH_SIZE", 100))
    )
    
    if config_dict.get("ARCHIVE_SCHEDULED", False):
        schedule_time = config_dict.get("ARCHIVE_SCHEDULE_TIME", "02:00")
        archiver.schedule_regular_archiving(schedule_time)
    else:
        archiver.run_archive_job()
