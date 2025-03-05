import time
import pinecone
import os
import random

# Initialize Pinecone (assumes environment variables are set)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-west1-gcp")
INDEX_NAME = os.getenv("PINECONE_INDEX", "benchmark-index")

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index = pinecone.Index(INDEX_NAME)

def generate_random_vector(dim=128):
    return [random.random() for _ in range(dim)]

def benchmark_pinecone_storage(num_contexts: int = 1000) -> dict:
    """
    Benchmark storage operations for conversation contexts in Pinecone.
    Returns:
      - total_time_seconds: total time taken for all upsert operations
      - average_time_per_operation_seconds: average time per individual operation
      - throughput_ops_per_second: number of operations per second
    """
    # Generate conversation contexts as (id, vector) pairs
    conversation_contexts = []
    for i in range(num_contexts):
        context_id = f"conv_{i+1}"
        vector = generate_random_vector()
        conversation_contexts.append((context_id, vector))
    
    start_time = time.perf_counter()
    for context_id, vector in conversation_contexts:
        index.upsert(items=[{"id": context_id, "values": vector}])
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    average_time = total_time / num_contexts if num_contexts else 0
    throughput = num_contexts / total_time if total_time > 0 else 0
    
    return {
        "total_time_seconds": total_time,
        "average_time_per_operation_seconds": average_time,
        "throughput_ops_per_second": throughput
    }

if __name__ == "__main__":
    metrics = benchmark_pinecone_storage()
    print("Benchmark Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")
