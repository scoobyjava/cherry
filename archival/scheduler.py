import json
import logging
import time
from datetime import datetime
import schedule

from pinecone_archiver import PineconeArchiver

# Configure logging
logging.basicConfig(
    filename="/var/log/cherry/scheduler.log",
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("archival_scheduler")

def run_archival_job():
    """Run the vector archival job"""
    logger.info("Starting scheduled vector archival job")
    start_time = time.time()
    
    try:
        archiver = PineconeArchiver()
        archiver.archive_old_vectors()
        archiver.close()
        
        execution_time = time.time() - start_time
        logger.info(f"Archival job completed successfully in {execution_time:.2f} seconds")
    except Exception as e:
        logger.error(f"Error running archival job: {str(e)}")


def setup_schedule():
    """Set up the job schedule based on configuration"""
    try:
        with open("/workspaces/cherry/archival/archival_config.json") as f:
            config = json.load(f)
        
        cron_schedule = config["archival"]["schedule"]
        parts = cron_schedule.split()
        
        # Parse cron expression (minute, hour, day, month, day_of_week)
        minute, hour, day, month, day_of_week = parts
        
        # Schedule job (supporting common cron patterns)
        job = schedule.every()
        
        # Day of month
        if day != "*":
            if "-" in day:
                start, end = map(int, day.split("-"))
                for d in range(start, end + 1):
                    job = schedule.every().day_at(f"{hour.zfill(2)}:{minute.zfill(2)}")
                    job.do(run_archival_job)
            else:
                job = job.day_at(f"{hour.zfill(2)}:{minute.zfill(2)}")
        # Day of week
        elif day_of_week != "*":
            days = {
                "0": schedule.every().sunday,
                "1": schedule.every().monday,
                "2": schedule.every().tuesday,
                "3": schedule.every().wednesday,
                "4": schedule.every().thursday,
                "5": schedule.every().friday,
                "6": schedule.every().saturday,
            }
            if day_of_week in days:
                job = days[day_of_week].at(f"{hour.zfill(2)}:{minute.zfill(2)}")
        # Daily
        else:
            job = job.day.at(f"{hour.zfill(2)}:{minute.zfill(2)}")
        
        job.do(run_archival_job)
        logger.info(f"Scheduled archival job with cron expression: {cron_schedule}")
    except Exception as e:
        logger.error(f"Failed to set up schedule: {str(e)}")
        # Default to daily at 3 AM if there's an error
        schedule.every().day.at("03:00").do(run_archival_job)
        logger.info("Using default schedule: daily at 03:00")


if __name__ == "__main__":
    logger.info("Starting archival scheduler")
    setup_schedule()
    
    # Run job immediately on startup (optional)
    run_archival_job()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)
