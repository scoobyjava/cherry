import numpy as np
import uuid
from typing import List, Dict, Any, Tuple


class VectorGenerator:
    """Generates synthetic vector data for benchmarking"""
    
    def __init__(self, dimensions=384, seed=42):
        self.dimensions = dimensions
        self.rng = np.random.RandomState(seed)
        
        # Define categories for metadata
        self.categories = [
            "news", "sports", "entertainment", "technology", 
            "science", "business", "health", "politics"
        ]
        
    def generate_vector(self) -> np.ndarray:
        """Generate a single normalized vector"""
        vec = self.rng.randn(self.dimensions)
        return vec / np.linalg.norm(vec)
        
    def generate_metadata(self) -> Dict[str, Any]:
        """Generate random metadata for a vector"""
        return {
            "id": str(uuid.uuid4()),
            "source_type": np.random.choice(["web", "pdf", "database", "api"]),
            "timestamp": int(np.floor(np.time())),
            "relevance_score": round(self.rng.uniform(0, 1), 2),
            "category": np.random.choice(self.categories),
            "document_id": f"doc-{self.rng.randint(1, 10000)}",
            "section_id": f"section-{self.rng.randint(1, 100)}",
            "confidence": round(self.rng.uniform(0.5, 1.0), 2)
        }
        
    def generate_dataset(self, size: int) -> List[Dict[str, Any]]:
        """Generate a dataset of vectors with metadata"""
        dataset = []
        
        for _ in range(size):
            vector = self.generate_vector()
            metadata = self.generate_metadata()
            
            dataset.append({
                "id": metadata["id"],
                "vector": vector.tolist(),
                "metadata": metadata
            })
            
        return dataset
        
    def generate_query_vectors(self, count: int) -> List[np.ndarray]:
        """Generate query vectors for search tests"""
        return [self.generate_vector() for _ in range(count)]
        
    def generate_search_filters(self, count: int) -> List[Dict]:
        """Generate metadata filters for filtered search tests"""
        filters = []
        
        for _ in range(count):
            filter_type = self.rng.randint(0, 3)
            
            if filter_type == 0:
                # Category filter
                filters.append({
                    "category": np.random.choice(self.categories)
                })
            elif filter_type == 1:
                # Source type filter
                filters.append({
                    "source_type": np.random.choice(["web", "pdf", "database", "api"])
                })
            else:
                # Relevance score range filter
                min_score = self.rng.uniform(0, 0.7)
                filters.append({
                    "relevance_score": {"$gte": min_score}
                })
                
        return filters
