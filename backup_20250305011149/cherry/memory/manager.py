import time
import uuid
from typing import Dict, List, Any, Optional, Union
from .base import MemoryInterface
from .factory import get_memory_provider

class MemoryManager:
    def __init__(self, primary_provider: str, primary_config: Dict[str, Any], 
                 cache_provider: Optional[str] = None, cache_config: Optional[Dict[str, Any]] = None,
                 cache_ttl: int = 3600):
        """
        Initialize memory manager with primary storage and optional cache
        
        Args:
            primary_provider: Main storage provider ("pinecone", "chroma")
            primary_config: Configuration for primary provider
            cache_provider: Optional cache provider
            cache_config: Configuration for cache provider
            cache_ttl: Cache time-to-live in seconds (default 1 hour)
        """
        self.primary = get_memory_provider(primary_provider, **primary_config)
        self.cache = get_memory_provider(cache_provider, **cache_config) if cache_provider else None
        self.cache_ttl = cache_ttl
        self.cache_index = {}  # Track TTL for cached items
        
    def generate_key(self) -> str:
        """Generate a unique memory key"""
        return str(uuid.uuid4())
        
    def store(self, data: Dict[str, Any], namespace: Optional[str] = None, key: Optional[str] = None) -> str:
        """Store data in memory with automatic key generation"""
        # Generate key if not provided
        memory_key = key if key else self.generate_key()
        
        # Add timestamp to data for context
        data["timestamp"] = int(time.time())
        
        # Store in primary storage
        self.primary.store(memory_key, data, namespace)
        
        # Cache if available
        if self.cache:
            self.cache.store(memory_key, data, namespace)
            self.cache_index[memory_key] = time.time() + self.cache_ttl
            
        return memory_key
        
    def retrieve(self, query: str, namespace: Optional[str] = None, limit: int = 5, 
                 recency_bias: float = 0.3) -> List[Dict[str, Any]]:
        """
        Retrieve memory with smart ranking that considers:
        - Semantic relevance
        - Recency
        - Importance (if specified in metadata)
        """
        # Get results from primary storage
        results = self.primary.retrieve(query, namespace, limit=limit*2)  # Fetch extra for reranking
        
        if not results:
            return []
            
        # Apply smart ranking
        current_time = time.time()
        for result in results:
            # Base score from vector similarity (already sorted)
            # Adjust for recency
            age_seconds = current_time - result.get("timestamp", current_time)
            recency_factor = 1.0 / (1.0 + (age_seconds / 86400) * recency_bias)  # Decay over days
            
            # Adjust for importance (if present)
            importance = result.get("metadata", {}).get("importance", 0.5)
            if isinstance(importance, str):
                importance_map = {"low": 0.3, "medium": 0.5, "high": 0.8, "critical": 1.0}
                importance = importance_map.get(importance.lower(), 0.5)
            
            # Calculate final score
            result["_score"] = result.get("_score", 0.8) * recency_factor * (1 + importance)
        
        # Re-rank and limit results
        results.sort(key=lambda x: x.get("_score", 0), reverse=True)
        return results[:limit]
        
    def update(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> bool:
        """Update existing memory entry"""
        # Update timestamp
        data["last_updated"] = int(time.time())
        
        # Update primary
        success = self.primary.update(key, data, namespace)
        
        # Update cache if available
        if success and self.cache:
            self.cache.update(key, data, namespace)
            self.cache_index[key] = time.time() + self.cache_ttl
            
        return success
        
    def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        """Remove a memory entry"""
        # Delete from primary
        success = self.primary.delete(key, namespace)
        
        # Delete from cache if available
        if success and self.cache:
            self.cache.delete(key, namespace)
            if key in self.cache_index:
                del self.cache_index[key]
                
        return success
        
    def maintain_cache(self) -> None:
        """Remove expired items from cache"""
        if not self.cache:
            return
            
        current_time = time.time()
        expired_keys = [k for k, v in self.cache_index.items() if v < current_time]
        
        for key in expired_keys:
            self.cache.delete(key)
            del self.cache_index[key]