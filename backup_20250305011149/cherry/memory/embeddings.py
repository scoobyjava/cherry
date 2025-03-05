import logging
from typing import List
import os
import time
import random
from typing import Any, Dict, Optional, Union, Callable

logger = logging.getLogger(__name__)

def generate_embedding(text: str) -> List[float]:
    """
    Generate an embedding vector for the given text.
    
    Args:
        text: The text to generate an embedding for
    
    Returns:
        A list of floats representing the embedding vector
    """
    try:
        # Determine which embedding model to use based on environment/config
        embedding_provider = os.environ.get("EMBEDDING_PROVIDER", "openai").lower()
        
        if embedding_provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            response = client.embeddings.create(
                input=text,
                model=os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
            )
            
            embedding = response.data[0].embedding
            
        elif embedding_provider == "huggingface":
            from sentence_transformers import SentenceTransformer
            
            model_name = os.environ.get("HUGGINGFACE_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            model = SentenceTransformer(model_name)
            embedding = model.encode(text).tolist()
            
        else:
            raise ValueError(f"Unsupported embedding provider: {embedding_provider}")
        
        logger.debug(f"Generated embedding of dimension {len(embedding)} for text")
        return embedding
        
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        raise

def batch_generate_embeddings(
    texts: List[str],
    generate_embedding_fn: Callable[[str], List[float]],
    batch_size: int = 20,
    max_retries: int = 10,
    initial_retry_delay: float = 1.0,
    jitter: float = 0.1,
    max_retry_delay: float = 60.0,
) -> List[List[float]]:
    """
    Generate embeddings for a list of texts in batches, handling rate limits gracefully.
    
    Args:
        texts: List of texts to generate embeddings for
        generate_embedding_fn: Function that generates an embedding for a single text
        batch_size: Number of texts to process in each batch
        max_retries: Maximum number of retry attempts for rate-limited requests
        initial_retry_delay: Initial delay in seconds before retrying
        jitter: Random jitter factor to add to delay (as a fraction of delay)
        max_retry_delay: Maximum delay between retries in seconds
        
    Returns:
        List of embeddings corresponding to the input texts
    """
    results = []
    
    # Process in batches
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = []
        
        # Process each text in the batch
        for text in batch:
            embeddings = None
            retries = 0
            delay = initial_retry_delay
            
            while embeddings is None and retries <= max_retries:
                try:
                    embeddings = generate_embedding_fn(text)
                except Exception as e:
                    retries += 1
                    
                    # Check if this appears to be a rate limit error
                    if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
                        if retries <= max_retries:
                            # Add some random jitter to the delay
                            actual_delay = delay * (1 + random.uniform(-jitter, jitter))
                            logger.warning(
                                f"Rate limit exceeded. Retrying in {actual_delay:.2f}s. "
                                f"Attempt {retries}/{max_retries}"
                            )
                            time.sleep(actual_delay)
                            
                            # Exponential backoff
                            delay = min(delay * 2, max_retry_delay)
                        else:
                            logger.error(f"Max retries exceeded for text: {text[:50]}...")
                            raise
                    else:
                        logger.error(f"Error generating embedding: {e}")
                        raise
            
            batch_embeddings.append(embeddings)
        
        results.extend(batch_embeddings)
        
        # Small pause between batches to avoid hitting rate limits
        if i + batch_size < len(texts):
            time.sleep(0.1)
    
    return results

def batch_generate_embeddings_parallel(
    texts: List[str],
    generate_embedding_fn: Callable[[List[str]], List[List[float]]],
    batch_size: int = 20,
    max_retries: int = 10,
    initial_retry_delay: float = 1.0,
    jitter: float = 0.1,
    max_retry_delay: float = 60.0,
) -> List[List[float]]:
    """
    Generate embeddings for a list of texts in batches using a function that supports
    parallel embedding generation, handling rate limits gracefully.
    
    Args:
        texts: List of texts to generate embeddings for
        generate_embedding_fn: Function that generates embeddings for a batch of texts at once
        batch_size: Number of texts to process in each batch
        max_retries: Maximum number of retry attempts for rate-limited requests
        initial_retry_delay: Initial delay in seconds before retrying
        jitter: Random jitter factor to add to delay (as a fraction of delay)
        max_retry_delay: Maximum delay between retries in seconds
        
    Returns:
        List of embeddings corresponding to the input texts
    """
    results = []
    
    # Process in batches
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = None
        retries = 0
        delay = initial_retry_delay
        
        while batch_embeddings is None and retries <= max_retries:
            try:
                batch_embeddings = generate_embedding_fn(batch)
            except Exception as e:
                retries += 1
                
                # Check if this appears to be a rate limit error
                if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
                    if retries <= max_retries:
                        # Add some random jitter to the delay
                        actual_delay = delay * (1 + random.uniform(-jitter, jitter))
                        logger.warning(
                            f"Rate limit exceeded. Retrying in {actual_delay:.2f}s. "
                            f"Attempt {retries}/{max_retries}"
                        )
                        time.sleep(actual_delay)
                        
                        # Exponential backoff
                        delay = min(delay * 2, max_retry_delay)
                    else:
                        logger.error(f"Max retries exceeded for batch starting with: {batch[0][:50]}...")
                        raise
                else:
                    logger.error(f"Error generating embeddings: {e}")
                    raise
        
        results.extend(batch_embeddings)
        
        # Small pause between batches to avoid hitting rate limits
        if i + batch_size < len(texts):
            time.sleep(0.1)
    
    return results
