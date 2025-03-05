"""
Example usage of the vector archival system.
"""
import os
from dotenv import load_dotenv
from cherry.data_management.archivers.vector_archiver import archive_old_vectors
from cherry.data_management.scheduler import setup_archival_scheduler

# Load environment variables
load_dotenv()

def run_manual_archival():
    """Run a manual archival process."""
    print("Running manual archival...")
    
    # Get Pinecone index name from environment variable or use default
    index_name = os.environ.get("PINECONE_INDEX", "my-index")
    
    # Archive vectors older than 6 months
    stats = archive_old_vectors(index_name, months=6)
    
    print(f"Archival completed:")
    print(f"Found: {stats.get('found_vectors', 0)} vectors")
    print(f"Archived: {stats.get('archived_vectors', 0)} vectors")
    print(f"Deleted: {stats.get('deleted_vectors', 0)} vectors")
    print(f"Time taken: {stats.get('elapsed_seconds', 0):.2f} seconds")
    
def run_scheduled_archival():
    """Setup and run scheduled archival."""
    print("Setting up scheduled archival...")
    
    # Get Pinecone index name from environment variable or use default
    index_name = os.environ.get("PINECONE_INDEX", "my-index")
    
    # Setup scheduler to run daily at 3 AM
    scheduler = setup_archival_scheduler(index_name, run_at_hour=3, run_at_minute=0)
    
    # Optionally run an initial archival
    print("Running initial archival...")
    stats = scheduler.run_now()
    
    print(f"Initial archival completed:")
    print(f"Found: {stats.get('found_vectors', 0)} vectors")
    print(f"Archived: {stats.get('archived_vectors', 0)} vectors")
    print(