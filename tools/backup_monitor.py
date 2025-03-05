
import json
import os
import sys
import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/workspaces/cherry/logs/backup_monitor.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("backup_monitor")

def load_config():
    """Load the benchmark configuration file"""
    config_path = Path("/workspaces/cherry/benchmarks/benchmark_config.json")
    if not config_path.exists():
        logger.error(f"Configuration file not found at {config_path}")
        return None
    
    with open(config_path, 'r') as f:
        return json.load(f)

def check_postgres_backups(config):
    """Check PostgreSQL backup status"""
    if not config.get('postgres', {}).get('backup', {}).get('enabled', False):
        logger.info("PostgreSQL backups not enabled, skipping check")
        return True
    
    backup_location = config['postgres']['backup']['location']
    retention_days = config['postgres']['backup']['retention_days']
    
    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_location):
        logger.warning(f"Backup location {backup_location} does not exist, creating it")
        os.makedirs(backup_location)
    
    # Check for recent backups
    now = datetime.datetime.now()
    backup_files = [f for f in os.listdir(backup_location) if f.startswith('backup_')]
    
    if not backup_files:
        logger.warning("No backup files found")
        return False
    
    # Get the most recent backup file
    latest_backup = max(backup_files)
    try:
        # Extract date from filename (assuming format backup_YYYYMMDD_HHMMSS.dump)
        date_str = latest_backup.replace('backup_', '').split('.')[0]
        backup_date = datetime.datetime.strptime(date_str, '%Y%m%d_%H%M%S')
        days_since_backup = (now - backup_date).days
        
        if days_since_backup > 1:
            logger.warning(f"Latest backup is {days_since_backup} days old")
            return False
        else:
            logger.info(f"Latest backup is from {backup_date}")
            
        # Clean old backups
        for backup_file in backup_files:
            try:
                date_str = backup_file.replace('backup_', '').split('.')[0]
                file_date = datetime.datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                file_age = (now - file_date).days
                
                if file_age > retention_days:
                    file_path = os.path.join(backup_location, backup_file)
                    logger.info(f"Deleting old backup: {file_path} ({file_age} days old)")
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Error processing backup file {backup_file}: {e}")
                
        return True
    except Exception as e:
        logger.error(f"Error checking backup date: {e}")
        return False

def check_replication_status(config):
    """Check replication status"""
    if not config.get('postgres', {}).get('replication', {}).get('enabled', False):
        logger.info("PostgreSQL replication not enabled, skipping check")
        return True
    
    # In a real environment, you would:
    # 1. Connect to PostgreSQL
    # 2. Check replication lag (pg_stat_replication view)
    # 3. Ensure all replicas are connected
    logger.info("Would check PostgreSQL replication status here")
    return True

def main():
    """Main monitoring function"""
    logger.info("Starting backup and replication monitoring")
    
    # Create logs directory if it doesn't exist
    os.makedirs("/workspaces/cherry/logs", exist_ok=True)
    
    config = load_config()
    if not config:
        return
    
    backup_status = check_postgres_backups(config)
    replication_status = check_replication_status(config)
    
    if not backup_status:
        logger.error("Backup check failed!")
    
    if not replication_status:
        logger.error("Replication check failed!")
    
    logger.info("Backup and replication monitoring complete")

if __name__ == "__main__":
    main()
