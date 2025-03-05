import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_env_file(env_file: str = ".env") -> bool:
    """
    Loads environment variables from a .env file.
    
    Args:
        env_file: Path to the .env file
        
    Returns:
        bool: True if the file was loaded, False otherwise
    """
    if os.path.exists(env_file):
        load_dotenv(env_file)
        logger.info(f"Loaded environment variables from {env_file}")
        return True
    else:
        logger.warning(f"Environment file {env_file} not found")
        return False

def get_required_env(name: str) -> str:
    """
    Get a required environment variable or raise an exception.
    
    Args:
        name: Name of the environment variable
        
    Returns:
        The environment variable value
        
    Raises:
        ValueError: If the environment variable is not set
    """
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Required environment variable '{name}' is not set")
    return value

def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get an environment variable with an optional default value.
    
    Args:
        name: Name of the environment variable
        default: Default value if not set
        
    Returns:
        The environment variable value or the default
    """
    return os.getenv(name, default)

def get_bool_env(name: str, default: bool = False) -> bool:
    """
    Get a boolean environment variable.
    
    Args:
        name: Name of the environment variable
        default: Default value if not set
        
    Returns:
        Boolean interpretation of the environment variable
    """
    value = os.getenv(name, str(default)).lower()
    return value in ('true', 't', '1', 'yes', 'y')

def get_int_env(name: str, default: Optional[int] = None) -> Optional[int]:
    """
    Get an integer environment variable.
    
    Args:
        name: Name of the environment variable
        default: Default value if not set
        
    Returns:
        Integer interpretation of the environment variable or the default
    """
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning(f"Environment variable {name} is not a valid integer: {value}")
        return default

def get_credentials(provider: str) -> Dict[str, Any]:
    """
    Get credentials for a specific provider from environment variables.
    
    Args:
        provider: The provider name (e.g., 'pinecone', 'chroma')
        
    Returns:
        Dictionary of credentials
    """
    credentials = {}
    
    if provider.lower() == 'pinecone':
        credentials['api_key'] = get_required_env('PINECONE_API_KEY')
        credentials['environment'] = get_required_env('PINECONE_ENVIRONMENT')
    
    elif provider.lower() == 'chroma':
        # Chroma might not need explicit credentials if using local instance
        credentials['host'] = get_env('CHROMA_HOST')
        credentials['port'] = get_int_env('CHROMA_PORT')
        if credentials['host'] is None:
            del credentials['host']
        if credentials['port'] is None:
            del credentials['port']
    
    elif provider.lower() in ['openai', 'anthropic']:
        api_key_env = f"{provider.upper()}_API_KEY"
        credentials['api_key'] = get_required_env(api_key_env)
    
    return credentials
