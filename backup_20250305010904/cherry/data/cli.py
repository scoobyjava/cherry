import argparse
import logging
import os
import sys
from typing import Dict, Any

from cherry.data.archive import run_archiver_from_config

logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Vector archiver for Pinecone to PostgreSQL")
    
    parser.add_argument("--pinecone-api-key", help="Pinecone API key")
    parser.add_argument("--pinecone-env", help="Pinecone environment")
    parser.add_argument("--pinecone-index", help="Pinecone index name")
    
    parser.add_argument("--postgres-host", help="PostgreSQL host", default="localhost")
    parser.add_argument("--postgres-port", help="PostgreSQL port", type=int, default=5432)
    parser.add_argument("--postgres-db", help="PostgreSQL database name")
    parser.add_argument("--postgres-user", help="PostgreSQL username")
    parser.add_argument("--postgres-password", help="PostgreSQL password")
    
    parser.add_argument("--archive-age", help="Age in months after which to archive vectors", 
                        type=int, default=6)
    parser.add_argument("--batch-size", help="Number of vectors to process in each batch", 
                        type=int, default=100)
    parser.add_argument("--schedule", help="Schedule archiving to run at specified time (HH:MM)",
                        default=None)
    
    return parser.parse_args()

def config_from_env() -> Dict[str, Any]:
    """Get configuration from environment variables."""
    return {
        "PINECONE_API_KEY": os.environ.get("PINECONE_API_KEY", ""),
        "PINECONE_ENVIRONMENT": os.environ.get("PINECONE_ENVIRONMENT", ""),
        "PINECONE_INDEX": os.environ.get("PINECONE_INDEX", ""),
        
        "POSTGRES_HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "POSTGRES_PORT": os.environ.get("POSTGRES_PORT", 5432),
        "POSTGRES_DB": os.environ.get("POSTGRES_DB", ""),
        "POSTGRES_USER": os.environ.get("POSTGRES_USER", ""),
        "POSTGRES_PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        
        "ARCHIVE_AGE_MONTHS": os.environ.get("ARCHIVE_AGE_MONTHS", 6),
        "ARCHIVE_BATCH_SIZE": os.environ.get("ARCHIVE_BATCH_SIZE", 100),
        "ARCHIVE_SCHEDULED": False,
        "ARCHIVE_SCHEDULE_TIME": os.environ.get("ARCHIVE_SCHEDULE_TIME", "02:00")
    }

def main():
    """Main entry point for the CLI."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Get configuration, prioritizing command line arguments
    args = parse_args()
    config = config_from_env()
    
    # Override with command line arguments if provided
    if args.pinecone_api_key:
        config["PINECONE_API_KEY"] = args.pinecone_api_key
    if args.pinecone_env:
        config["PINECONE_ENVIRONMENT"] = args.pinecone_env
    if args.pinecone_index:
        config["PINECONE_INDEX"] = args.pinecone_index
        
    if args.postgres_host:
        config["POSTGRES_HOST"] = args.postgres_host
    if args.postgres_port:
        config["POSTGRES_PORT"] = args.postgres_port
    if args.postgres_db:
        config["POSTGRES_DB"] = args.postgres_db
    if args.postgres_user:
        config["POSTGRES_USER"] = args.postgres_user
    if args.postgres_password:
        config["POSTGRES_PASSWORD"] = args.postgres_password
        
    if args.archive_age:
        config["ARCHIVE_AGE_MONTHS"] = args.archive_age
    if args.batch_size:
        config["ARCHIVE_BATCH_SIZE"] = args.batch_size
    if args.schedule:
        config["ARCHIVE_SCHEDULED"] = True
        config["ARCHIVE_SCHEDULE_TIME"] = args.schedule
    
    # Validate required configuration
    required_keys = [
        "PINECONE_API_KEY", "PINECONE_ENVIRONMENT", "PINECONE_INDEX",
        "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"
    ]
    
    missing_keys = [key for key in required_keys if not config[key]]
    if missing_keys:
        logger.error(f"Missing required configuration: {', '.join(missing_keys)}")
        sys.exit(1)
    
    # Run the archiver
    run_archiver_from_config(config)

if __name__ == "__main__":
    main()
