import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import logging
import os
import json
from typing import List, Dict, Any
import openai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Load model and tokenizer for embedding generation
model_name = "sentence-transformers/all-mpnet-base-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Set up logging
logger = logging.getLogger(__name__)

def load_config() -> Dict[str, Any]:
    """
    Load configuration from the benchmark_config.json file.
    
    Returns:
        Dict[str, Any]: Configuration dictionary.
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "benchmarks", "benchmark_config.json")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        raise

def initialize_openai_client() -> openai.OpenAI:
    """Initialize the OpenAI client with the key from configuration."""
    config = load_config()
    api_key = config.get("openai", {}).get("api_key", "")
    
    # Handle potential secret placeholders
    if api_key.startswith("${SECRET:"):
        # In a real environment, this would be replaced by the actual secret
        # For now, fall back to environment variable
        api_key = os.environ.get("OPENAI_API_KEY", "")
    
    if not api_key:
        raise ValueError("OpenAI API key is not set in configuration or environment variables")
    
    # Set organization ID if available
    org_id = config.get("openai", {}).get("organization_id", "")
    if org_id and org_id.startswith("${SECRET:"):
        org_id = os.environ.get("OPENAI_ORG_ID", "")
    
    # Create and return the client
    return openai.OpenAI(
        api_key=api_key,
        organization=org_id if org_id else None
    )

# Get a global client instance
_client = None

def get_openai_client() -> openai.OpenAI:
    """Get or create an OpenAI client instance."""
    global _client
    if (_client is None):
        _client = initialize_openai_client()
    return _client

# Define exception types to retry on
retry_on_exceptions = (
    openai.APITimeoutError,
    openai.APIError,
    openai.APIConnectionError,
    openai.RateLimitError,
)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type(retry_on_exceptions),
    reraise=True
)
def generate_embedding(text: str) -> List[float]:
    """
    Generate a 1536-dimensional embedding vector from the input text using OpenAI's text-embedding-ada-002 model.
    
    Args:
        text (str): The input text to embed.
        
    Returns:
        List[float]: A 1536-dimensional embedding vector.
        
    Raises:
        ValueError: If the input text is empty or None.
        openai.AuthenticationError: If the API key is invalid.
        Exception: For other unexpected errors.
    """
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty or None")
    
    client = get_openai_client()
    
    try:
        # Call OpenAI's embedding API
        response = client.embeddings.create(
            input=text.strip(),
            model="text-embedding-ada-002"
        )
        
        # Extract the embedding from the response
        embedding = response.data[0].embedding
        
        # Ensure the embedding is of the expected dimension
        if len(embedding) != 1536:
            logger.warning(f"Expected embedding dimension 1536, but got {len(embedding)}")
            
        return embedding
        
    except openai.AuthenticationError as e:
        logger.error(f"Authentication error: {str(e)}")
        raise
        
    except openai.RateLimitError as e:
        logger.warning(f"Rate limit exceeded: {str(e)}")
        raise
        
    except (openai.APIError, openai.APIConnectionError) as e:
        logger.warning(f"API error: {str(e)}")
        raise
        
    except openai.APITimeoutError as e:
        logger.warning(f"Request timed out: {str(e)}")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error generating embedding: {str(e)}")
        raise
