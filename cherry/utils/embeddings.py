import os
import numpy as np
from typing import List, Optional

def get_embedding(text: str, model: str = "text-embedding-ada-002") -> List[float]:
    """Generate embedding for text using specified model"""
    # Placeholder implementation - replace with actual embedding code
    # In production, use OpenAI API, SentenceTransformers, or similar
    dimension = get_embedding_dimension(model)
    # Generate random vector for demonstration purposes
    return list(np.random.normal(0, 1, dimension).astype(float))

def get_embedding_dimension(model: str = "text-embedding-ada-002") -> int:
    """Return the dimension of embeddings for the given model"""
    dimensions = {
        "text-embedding-ada-002": 1536,
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072
    }
    return dimensions.get(model, 1536)
