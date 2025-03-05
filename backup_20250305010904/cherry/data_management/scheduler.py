"""
Scheduler for running data management tasks periodically.
"""
import os
import time
import schedule
import threading
from datetime import datetime
from typing import Callable, Dict, Any, Optional

from cherry.data_management.archivers.vector_archiver import archive_old_vectors
from logger import get_logger

logger = get_logger(__name__)

class ArchivalScheduler:
    """Scheduler for vector archival tasks."""
    
    def __init__(self, pinecone_index: str):
        """
        Initialize scheduler.
        
        Args:
            pinecone_index: Name of the Pinecone index to archive from.
        """
        self.pinecone_index = pinecone_index
        self.running = False
        self.scheduler_thread = None
        
    def start(self, run_at_hour: int = 2, run_at_minute: int = 0):
        """
        Start the scheduler.
        
        Args:
            run_at_hour: Hour of day to run the archival (24-hour format).
            run_at_minute: Minute of hour to run the archival.
        """
        if self.running:
            logger.warning("Scheduler is already running")
            return
            
        # Schedule the archival job to run daily at specified time
        schedule_time = f"{run_at_hour:02d}:{run_at_minute:02d}"
        schedule.every().day.at(schedule_time).do(self._run_archival)
        
        logger.info(f"Scheduled vector archival to run daily at {schedule_time}")
        
        # Start the scheduler in a separate thread
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=1.0)
        schedule.clear()
        logger.info("Archival scheduler stopped")
        
    def _run_scheduler(self):
        """Run the scheduler loop."""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    def _run_archival(self):
        """Run the archival job."""
        try:
            logger.info(f"Starting scheduled archival for index {self.pinecone_index}")
            stats = archive_old_vectors(self.pinecone_index)
            logger.info(f"Scheduled archival completed: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error during scheduled archival: {e}")
            return {"error": str(e)}
            
    def run_now(self) -> Dict[str, Any]:
        """
        Run the archival job immediately.
        
        Returns:
            Archival statistics.
        """
        return self._run_archival()


def setup_archival_scheduler(
    pinecone_index: str,
    run_at_hour: int = 2,  # Run at 2 AM by default
    run_at_minute: int = 0
) -> ArchivalScheduler:
    """
    Setup and start the archival scheduler.
    
    Args:
        pinecone_index: Name of the Pinecone index.
        run_at_hour: Hour of day to run the archival (24-hour format).
        run_at_minute: Minute of hour to run the archival.
        
    Returns:
        Archival scheduler instance.
    """
    scheduler = ArchivalScheduler(pinecone_index)
    scheduler.start(run_at_hour, run_at_minute)
    return scheduler
