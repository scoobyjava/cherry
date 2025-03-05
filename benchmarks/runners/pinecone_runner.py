import time
import pinecone
import numpy as np
from typing import List, Dict, Any
from utils.metrics import BenchmarkResult


class PineconeRunner:
    """Runs benchmarks for Pinecone vector database"""
    
    def __init__(self, config):
        self.config = config
        self.index_name = config["index_name"]
        self.namespace = "search_agent"  # Using the search_agent namespace from config
        
        # Initialize Pinecone
        pinecone.init(
            api_key=config["api_key"],
            environment=config["environment"]
        )
        
        # Create index if it doesn't exist
        if self.index_name not in pinecone.list_indexes():
            print(f"Creating Pinecone index '{self.index_name}'...")
            pinecone.create_index(
                name=self.index_name,
                dimension=384,
                metric="cosine"
            )
        
        self.index = pinecone.Index(self.index_name)
        
    def insert_vectors(self, dataset: List[Dict[str, Any]]) -> float:
        """Insert vectors into Pinecone and return time taken"""
        start_time = time.time()
        
        # Convert to Pinecone format
        vectors = []
        batch_size = 100  # Pinecone batch size limit
        
        for item in dataset:
            vectors.append((
                item["id"],
                item["vector"],
                item["metadata"]
            ))
            
            # Upsert in batches
            if len(vectors) >= batch_size:
                self.index.upsert(vectors=vectors, namespace=self.namespace)
                vectors = []
                
        # Upsert remaining vectors
        if vectors:
            self.index.upsert(vectors=vectors, namespace=self.namespace)
            
        return time.time() - start_time
        
    def benchmark_search(self, query_vectors: List[np.ndarray], top_k=5) -> Dict:
        """Benchmark simple vector search"""
        result = BenchmarkResult(
            test_name="simple_search",
            system_name="pinecone",
            dataset_size=self.index.describe_index_stats().total_vector_count
        )
        
        for i, vector in enumerate(query_vectors):
            start_time = time.time()
            self.index.query(
                vector=vector.tolist(),
                top_k=top_k,
                namespace=self.namespace
            )
            latency = time.time() - start_time
            result.latencies.append(latency)
            
        return result.to_dict()
        
    def benchmark_filtered_search(self, query_vectors: List[np.ndarray], top_k=5) -> Dict:
        """Benchmark filtered vector search"""
        result = BenchmarkResult(
            test_name="filtered_search",
            system_name="pinecone",
            dataset_size=self.index.describe_index_stats().total_vector_count
        )
        
        # Cycle through different filter types
        filter_types = [
            {"category": "technology"},
            {"source_type": "web"},
            {"relevance_score": {"$gte": 0.5}}
        ]
        
        for i, vector in enumerate(query_vectors):
            filter_dict = filter_types[i % len(filter_types)]
            
            start_time = time.time()
            self.index.query(
                vector=vector.tolist(),
                top_k=top_k,
                namespace=self.namespace,
                filter=filter_dict
            )
            latency = time.time() - start_time
            result.latencies.append(latency)
            
        return result.to_dict()
        
    def cleanup(self):
        """Clean up resources after benchmarking"""
        # Delete all vectors in the namespace
        try:
            stats = self.index.describe_index_stats()
            if stats.namespaces.get(self.namespace, {}).get('vector_count', 0) > 0:
                self.index.delete(delete_all=True, namespace=self.namespace)
                print(f"Cleaned up Pinecone namespace '{self.namespace}'")
        except Exception as e:
            print(f"Error cleaning up Pinecone: {str(e)}")
