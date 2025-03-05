#!/usr/bin/env python3
"""
Script to archive or delete old vectors from Pinecone to PostgreSQL.
Can be run as a one-time job or scheduled task.
"""

import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cherry.data.archive import VectorArchiver, run_archiver_from_config
import config

def main():
    """Main entry point for the script."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/vector_archiving.log")
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting vector archiving process")
    
    # Create configuration dictionary
    config_dict = {
        "PINECONE_API_KEY": config.PINECONE_API_KEY,
        "PINECONE_ENVIRONMENT": config.PINECONE_ENVIRONMENT,
        "PINECONE_INDEX": config.PINECONE_INDEX,
        
        "POSTGRES_HOST": config.POSTGRES_HOST,
        "POSTGRES_PORT": config.POSTGRES_PORT,
        "POSTGRES_DB": config.POSTGRES_DB,
        "POSTGRES_USER": config.POSTGRES_USER,
        "POSTGRES_PASSWORD": config.POSTGRES_PASSWORD,
        
        "ARCHIVE_AGE_MONTHS": config.ARCHIVE_AGE_MONTHS,
        "ARCHIVE_BATCH_SIZE": config.ARCHIVE_BATCH_SIZE,
        "ARCHIVE_SCHEDULED": len(sys.argv) > 1 and sys.argv[1] == "--schedule",
        "ARCHIVE_SCHEDULE_TIME": config.ARCHIVE_SCHEDULE_TIME
    }
    
    # Run the archiver
    run_archiver_from_config(config_dict)
    
    logger.info("Vector archiving process completed")

if __name__ == "__main__":
    main()
