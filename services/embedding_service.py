import os
import logging
import openai
import time
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, config: Dict[str, Any]):
        """Initialize OpenAI embedding service with config"""
        self.config = config
        
        # Process API key that might be a reference to a secret
        api_key = self._process_config_value(config["api_key"])
        org_id = self._process_config_value(config.get("organization_id", ""))
        
        # Set up OpenAI client
        openai.api_key = api_key
        if org_id:
            openai.organization = org_id
        
        # Default embedding model
        self.embedding_model = "text-embedding-ada-002"
        
        logger.info("Initialized embedding service")
    
    def _process_config_value(self, value: str) -> str:
        """Process configuration values that might contain references to secrets"""
        if isinstance(value, str) and value.startswith("${SECRET:") and value.endswith("}"):
            secret_name = value[9:-1]
            return os.environ.get(secret_name, "")
        return value
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of text inputs"""
        if not texts:
            return []
            
        results = []
        batch_size = 20  # OpenAI recommends batching for efficiency
        
        # Process in batches to avoid rate limits and improve efficiency
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            
            retries = 0
            max_retries = 3
            backoff_factor = 2
            
            while retries <= max_retries:
                try:
                    response = openai.Embedding.create(
                        input=batch_texts,
                        model=self.embedding_model
                    )
                    
                    # Extract embeddings from response
                    batch_embeddings = [item["embedding"] for item in response["data"]]
                    results.extend(batch_embeddings)
                    
                    # Log success
                    logger.info(f"Successfully generated {len(batch_embeddings)} embeddings")
                    
                    # Break out of retry loop on success
                    break
                    
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Failed to generate embeddings after {max_retries} retries: {str(e)}")
                        raise
                    
                    # Exponential backoff
                    sleep_time = backoff_factor ** retries
                    logger.warning(f"Error generating embeddings: {str(e)}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
        
        return results
