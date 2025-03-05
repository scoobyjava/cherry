import time
import logging
import json
import os
from typing import List, Dict, Any, Optional, Union, Callable
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Assuming generate_embedding is imported from elsewhere
# from .embedding import generate_embedding

logger = logging.getLogger(__name__)

class OpenAIRateLimitError(Exception):
    """Exception raised when OpenAI rate limits are hit."""
    pass

def load_config():
    """Load configuration from benchmark_config.json"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              "benchmarks", "benchmark_config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
    return config

def batch_generate_embeddings(
    texts: List[str],
    generate_embedding_fn: Callable[[str], List[float]] = None,
    batch_size: int = 20,
    max_retries: int = 5,
    initial_backoff: float = 1.0,
    max_backoff: float = 60.0,
    concurrent_batches: int = 1,
    show_progress: bool = True
) -> List[List[float]]:
    """
    Generate embeddings for a list of texts in batches, handling rate limits.
    
    Args:
        texts: List of text strings to generate embeddings for
        generate_embedding_fn: Function to call for generating a single embedding
        batch_size: Number of texts to process in each batch
        max_retries: Maximum number of retry attempts per batch
        initial_backoff: Initial backoff time in seconds
        max_backoff: Maximum backoff time in seconds
        concurrent_batches: Number of batches to process concurrently
        show_progress: Whether to show a progress bar
    
    Returns:
        List of embedding vectors
    """
    if generate_embedding_fn is None:
        # Default to the imported generate_embedding function
        from .embedding import generate_embedding
        generate_embedding_fn = generate_embedding
    
    total_texts = len(texts)
    all_embeddings = [None] * total_texts  # Pre-allocate results list
    
    def process_batch(batch_idx: int):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, total_texts)
        batch_texts = texts[start_idx:end_idx]
        batch_embeddings = []
        
        retries = 0
        backoff_time = initial_backoff
        
        while retries <= max_retries:
            try:
                # Process each text in the batch individually
                for text in batch_texts:
                    embedding = generate_embedding_fn(text)
                    batch_embeddings.append(embedding)
                
                # If successful, break out of retry loop
                break
            
            except Exception as e:
                # Check if it's a rate limit error
                if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
                    if retries == max_retries:
                        raise OpenAIRateLimitError(f"Max retries ({max_retries}) exceeded for batch {batch_idx}")
                    
                    logger.warning(f"Rate limit hit on batch {batch_idx}. Retrying in {backoff_time}s...")
                    time.sleep(backoff_time)
                    
                    # Exponential backoff with jitter
                    backoff_time = min(backoff_time * 2, max_backoff)
                    retries += 1
                else:
                    # Re-raise if it's not a rate limit error
                    logger.error(f"Error processing batch {batch_idx}: {str(e)}")
                    raise
        
        # Store results in correct positions
        for i, embedding in enumerate(batch_embeddings):
            all_embeddings[start_idx + i] = embedding
            
        return batch_embeddings
    
    # Create batches
    num_batches = (total_texts + batch_size - 1) // batch_size  # Ceiling division
    
    if show_progress:
        pbar = tqdm(total=total_texts, desc="Generating embeddings")
    
    if concurrent_batches > 1:
        # Process batches concurrently
        with ThreadPoolExecutor(max_workers=concurrent_batches) as executor:
            futures = []
            for batch_idx in range(num_batches):
                futures.append(executor.submit(process_batch, batch_idx))
            
            # Wait for results and update progress
            for future in futures:
                batch_result = future.result()
                if show_progress:
                    pbar.update(len(batch_result))
    else:
        # Process batches sequentially
        for batch_idx in range(num_batches):
            batch_result = process_batch(batch_idx)
            if show_progress:
                pbar.update(len(batch_result))
    
    if show_progress:
        pbar.close()
        
    return all_embeddings

def batch_generate_embeddings_with_metadata(
    texts: List[str],
    metadata_list: Optional[List[Dict[str, Any]]] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Generate embeddings with associated metadata in batches.
    
    Args:
        texts: List of text strings to generate embeddings for
        metadata_list: Optional list of metadata dictionaries, one per text
        **kwargs: Additional arguments to pass to batch_generate_embeddings
    
    Returns:
        List of dictionaries containing embeddings and metadata
    """
    embeddings = batch_generate_embeddings(texts, **kwargs)
    
    results = []
    for i, embedding in enumerate(embeddings):
        result = {
            "embedding": embedding,
            "text": texts[i]
        }
        
        # Add metadata if provided
        if metadata_list and i < len(metadata_list):
            result["metadata"] = metadata_list[i]
            
        results.append(result)
        
    return results
