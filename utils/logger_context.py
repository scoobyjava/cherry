import logging
import json
import time

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("application.log"),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)

# Create a named logger
logger = logging.getLogger('cherry')

# Helper function to log structured data
def log_json(data, message="Structured data"):
    formatted_json = json.dumps(data, indent=2)
    logger.info(f"{message}:\n{formatted_json}")

# System initialization sequence
logger.info("🚀 System initialization sequence started")
logger.info("📂 Loading configuration files")
logger.info("🔌 Establishing database connections")
logger.info("⚙️ Registering service handlers")
logger.info("✅ System initialization complete")

# Resource warning
resource_info = {
    "resource_type": "memory",
    "current_usage": "85%",
    "threshold": "80%",
    "instance_id": "worker-03"
}
logger.warning(f"⚠️ Resource threshold exceeded: {resource_info}")

# Task details logging
task_details = {
    "id": "task-a7f392",
    "type": "data_processing",
    "parameters": {
        "input_file": "dataset.csv",
        "filters": ["date > 2025-01-01", "status = active"],
        "output_format": "json"
    },
    "priority": "high",
    "timeout_seconds": 300
}
log_json(task_details, "🔄 Processing task with details")

# Audit logging
audit_data = {
    "user": "admin",
    "action": "config_change",
    "timestamp": "2025-03-03T18:00:00Z",
    "changes": {
        "before": {"max_workers": 5},
        "after": {"max_workers": 10}
    },
    "source_ip": "192.168.1.100"
}
log_json(audit_data, "🔒 Audit log entry")

# Performance logging
start_time = time.time()
time.sleep(0.5)  # Simulate task delay
duration = time.time() - start_time
logger.info(f"⏱️ Operation completed in {duration:.3f} seconds")