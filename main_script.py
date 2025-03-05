import logging
import time
import json
import random
from logging.handlers import TimedRotatingFileHandler
import traceback
import functools
import os

# 1. Set up logging with both timestamped filename and rotation
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create a timestamp for the current log file
timestamp = time.strftime('%Y%m%d_%H%M%S')
log_filename = f"{log_dir}/application_{timestamp}.log"

# Configure handlers
file_handler = logging.FileHandler(log_filename)
console_handler = logging.StreamHandler()

# Common formatter for both handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Configure the root logger
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[file_handler, console_handler]
)

# Get a named logger
logger = logging.getLogger('cherry')

# 2. Helper functions for better logging
def log_json(data, message="Structured data"):
    """Format and log JSON data with proper indentation"""
    formatted_json = json.dumps(data, indent=2)
    logger.info(f"{message}:\n{formatted_json}")

def log_func(func):
    """Decorator to log function calls with parameters and return values"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"🔍 Calling {func.__name__} with args={args}, kwargs={kwargs}")
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"✅ {func.__name__} returned {result} in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ {func.__name__} failed after {duration:.3f}s with error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    return wrapper

# 3. Sample functions to demonstrate logging
@log_func
def compute_value(x, y):
    """Sample function that might fail"""
    time.sleep(0.2)  # Simulate processing time
    return x / y

@log_func
def process_data(data_id, options=None):
    """Process data with various options"""
    if options is None:
        options = {}
    
    # Log the start of processing
    logger.info(f"🔄 Starting to process data_id={data_id}")
    
    # Sample audit log
    audit_data = {
        "user_id": "user_" + str(random.randint(1000, 9999)),
        "action": "data_processing",
        "data_id": data_id,
        "options": options,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    log_json(audit_data, "📝 Audit entry for data processing")
    
    # Simulate processing time
    time.sleep(0.3)
    
    # Random chance of warning
    if random.random() < 0.3:  # 30% chance
        logger.warning(f"⚠️ Processing data_id={data_id} is taking longer than expected")
    
    # Log completion
    logger.info(f"✅ Completed processing data_id={data_id}")
    return {"status": "completed", "data_id": data_id}

# 4. Main execution demonstrates different log levels and scenarios
def main():
    logger.info(f"🚀 Application started with log file: {log_filename}")
    
    # Log system info
    system_info = {
        "python_version": "3.12.1",
        "environment": "development",
        "config_file": "settings.json",
        "log_level": "DEBUG"
    }
    log_json(system_info, "🔧 System information")
    
    # Demonstrate all log levels
    logger.debug("🔍 This is a DEBUG message - for detailed troubleshooting")
    logger.info("ℹ️ This is an INFO message - for general information")
    logger.warning("⚠️ This is a WARNING message - for potential issues")
    logger.error("❌ This is an ERROR message - for issues that prevent normal operation")
    logger.critical("🔥 This is a CRITICAL message - for severe errors that may cause crashes")
    
    # Process multiple data items
    for i in range(3):
        data_id = f"data_{random.randint(1000, 9999)}"
        options = {
            "format": random.choice(["json", "xml", "csv"]),
            "compress": random.choice([True, False]),
            "priority": random.choice(["high", "medium", "low"])
        }
        
        try:
            process_data(data_id, options)
        except Exception as e:
            logger.error(f"❌ Failed to process {data_id}: {str(e)}")
    
    # Demonstrate error handling
    try:
        # This will raise a ZeroDivisionError
        result = compute_value(10, 0)
    except Exception as e:
        logger.error(f"❌ Error in main workflow: {str(e)}")
    
    # Successful computation
    try:
        result = compute_value(10, 2)
        logger.info(f"✅ Computation successful with result: {result}")
    except Exception as e:
        logger.error(f"❌ Unexpected error in computation: {str(e)}")
    
    logger.info("👋 Application shutting down normally")
