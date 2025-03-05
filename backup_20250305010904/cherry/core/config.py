import os
from typing import Dict, Any

def get_database_config() -> Dict[str, Any]:
    """
    Get database connection configuration from environment variables
    
    Returns:
        Dictionary containing database connection parameters
    """
    return {
        "dbname": os.environ.get("POSTGRES_DB", "cherry_db"),
        "user": os.environ.get("POSTGRES_USER", "postgres"),
        "password": os.environ.get("POSTGRES_PASSWORD", ""),
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": os.environ.get("POSTGRES_PORT", "5432"),
    }
