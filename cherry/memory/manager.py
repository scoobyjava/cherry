import time
import uuid
from typing import Dict, List, Any, Optional
from .factory import get_memory_provider

class MemoryManager:
    def __init__(self, primary_provider: str, primary_config: Dict[str, Any],
                 cache_provider: Optional[str] = None, cache_config: Optional[Dict[str, Any]] = None,
                 cache_ttl: int = 3600):
        """
        Initialize memory manager with primary storage and optional cache.
        
        Args:
            primary_provider: Main storage provider ("pinecone", "chroma").
            primary_config: Configuration dictionary for primary provider.
            cache_provider: Optional cache provider type.
            cache_config: Configuration dictionary for cache provider.
            cache_ttl: Cache time-to-live in seconds (default 1 hour).
        """
        self.primary = get_memory_provider(primary_provider, **primary_config)
        self.cache = get_memory_provider(cache_provider, **cache_config) if cache_provider else None
        self.cache_ttl = cache_ttl
        self.cache_index: Dict[str, float] = {}  # Mapping of key to expiration timestamp

    def generate_key(self) -> str:
        """Generate a unique memory key."""
        return str(uuid.uuid4())

    def store(self, data: Dict[str, Any], namespace: Optional[str] = None, key: Optional[str] = None) -> str:
        """Store data in memory with an automatically generated key (if none provided)."""
        memory_key = key if key else self.generate_key()
        # Add a timestamp to the data for recency ranking
        data["timestamp"] = int(time.time())

        # Store data in primary storage
        self.primary.store(memory_key, data, namespace)

        # Also store in cache if available
        if self.cache:
            self.cache.store(memory_key, data, namespace)
            self.cache_index[memory_key] = time.time() + self.cache_ttl

        return memory_key

    def retrieve(self, query: str, namespace: Optional[str] = None, limit: int = 5,
                 recency_bias: float = 0.3) -> List[Dict[str, Any]]:
        """
        Retrieve memory entries matching the query and apply smart ranking based on recency and importance.
        
        Args:
            query: The search query.
            namespace: Optional namespace to restrict search.
            limit: Number of results to return.
            recency_bias: Factor tuning the decay of older entries.
        
        Returns:
            List of memory entries (each as a dict).
        """
        # Fetch more than needed and then re-rank
        results = self.primary.retrieve(query, namespace, limit=limit * 2)

        if not results:
            return []

        current_time = time.time()
        for result in results:
            # Use the stored timestamp, if available; default to current_time otherwise
            timestamp = result.get("timestamp", current_time)
            age_seconds = current_time - timestamp
            # Calculate a recency factor that decays over days
            recency_factor = 1.0 / (1.0 + (age_seconds / 86400) * recency_bias)

            # Determine importance, mapping string values appropriately
            importance = result.get("metadata", {}).get("importance", 0.5)
            if isinstance(importance, str):
                importance_map = {"low": 0.3, "medium": 0.5, "high": 0.8, "critical": 1.0}
                importance = importance_map.get(importance.lower(), 0.5)

            base_score = result.get("_score", 0.8)
            # Final score combines base score, recency, and importance
            result["_score"] = base_score * recency_factor * (1 + importance)

        # Sort results by computed score and return top 'limit' entries
        results.sort(key=lambda x: x.get("_score", 0), reverse=True)
        return results[:limit]

    def update(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> bool:
        """Update an existing memory entry."""
        data["last_updated"] = int(time.time())
        success = self.primary.update(key, data, namespace)
        if success and self.cache:
            self.cache.update(key, data, namespace)
            self.cache_index[key] = time.time() + self.cache_ttl
        return success

    def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        """Delete a memory entry."""
        success = self.primary.delete(key, namespace)
        if success and self.cache:
            self.cache.delete(key, namespace)
            self.cache_index.pop(key, None)
        return success

    def maintain_cache(self) -> None:
        """Remove expired items from the cache."""
        if not self.cache:
            return
        current_time = time.time()
        expired_keys = [k for k, expiry in self.cache_index.items() if expiry < current_time]
        for key in expired_keys:
            self.cache.delete(key)
            del self.cache_index[key]