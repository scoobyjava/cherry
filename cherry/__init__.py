"""
Cherry - AI Orchestration Framework
"""
import os
import logging
from cherry.utils.env import load_env_file

# Configure logging
logging.basicConfig(
    level=os.getenv("CHERRY_LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Load environment variables from .env file if available
default_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_env_file(default_env_path)

# Set version
__version__ = "0.1.0"
