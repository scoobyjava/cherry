"""
Benchmark script for measuring latency and accuracy of memory retrieval methods
across different Pinecone index sizes.
"""

import time
import random
import statistics
import argparse
from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

# Assuming this is the correct import path based on your project structure
from cherry.memory.vector_store import PineconeMemory

class MemoryRetrievalBenchmark:
    """Benchmark for memory retrieval methods with varying index sizes."""
    
    def __init__(self, index_sizes: List[int] = None):
        """
        Initialize the benchmark.
        
        Args:
            index_sizes: List of index sizes to benchmark (number of entries)
        """
        self.index_sizes = index_sizes or [1000, 10000, 100000]
        self.memories = {}
        self.results = {
            "size": [],
            "latency_mean": [],
            "latency_p50": [],
            "latency_p90": [],
            "latency_p99": [],
            "accuracy": [],
        }

    async def setup_indexes(self):
        """Create and populate test indexes of different sizes."""
        print("Setting up test indexes...")
        
        for size in self.index_sizes:
            print(f"Creating index with {size} entries...")
            namespace = f"benchmark_{size}"
            
            # Initialize memory with a dedicated namespace for benchmarking
            memory = PineconeMemory(namespace=namespace)
            
            # Generate synthetic data
            await self._populate_index(memory, size)
            
            # Store memory instance for later use
            self.memories[size] = memory
            
        print("Setup complete.")

    async def _populate_index(self, memory: PineconeMemory, size: int):
        """
        Populate an index with synthetic data.
        
        Args:
            memory: The memory instance to populate
            size: Number of entries to add
        """
        # Create synthetic documents with embeddings
        batch_size = min(100, size)
        
        with tqdm(total=size, desc=f"Populating {size} entries") as pbar:
            for i in range(0, size, batch_size):
                batch_count = min(batch_size, size - i)
                
                # Create batch of documents
                docs = []
                for j in range(batch_count):
                    doc_id = f"doc_{i+j}"
                    # Create synthetic document with random content
                    content = f"This is test document {doc_id} with random content {random.randint(1, 1000)}"
                    # For benchmarking purposes, we'll use random vectors
                    # In a real scenario, these would be meaningful embeddings
                    embedding = np.random.rand(384).tolist()  # Common embedding size
                    
                    docs.append({
                        "id": doc_id,
                        "content": content,
                        "embedding": embedding,
                        "metadata": {"source": "benchmark", "category": random.choice(["A", "B", "C"])}
                    })
                
                # Add documents to memory
                await memory.add_many(docs)
                pbar.update(batch_count)

    async def run_latency_benchmark(self, num_queries: int = 50):
        """
        Run latency benchmarks for different index sizes.
        
        Args:
            num_queries: Number of queries to run for each index size
        """
        print("\nRunning latency benchmarks...")
        
        for size, memory in self.memories.items():
            print(f"Testing index with {size} entries...")
            latencies = []
            
            # Generate random query vectors
            query_vectors = [np.random.rand(384).tolist() for _ in range(num_queries)]
            
            # Run queries and measure latency
            for query_vector in tqdm(query_vectors, desc="Queries"):
                start_time = time.time()
                results = await memory.retrieve_design_memories(query_vector, top_k=5)
                end_time = time.time()
                
                latency = (end_time - start_time) * 1000  # Convert to ms
                latencies.append(latency)
            
            # Calculate statistics
            mean_latency = statistics.mean(latencies)
            p50_latency = np.percentile(latencies, 50)
            p90_latency = np.percentile(latencies, 90)
            p99_latency = np.percentile(latencies, 99)
            
            print(f"Results for {size} entries:")
            print(f"  Mean latency: {mean_latency:.2f} ms")
            print(f"  P50 latency: {p50_latency:.2f} ms")
            print(f"  P90 latency: {p90_latency:.2f} ms")
            print(f"  P99 latency: {p99_latency:.2f} ms")
            
            # Store results
            self.results["size"].append(size)
            self.results["latency_mean"].append(mean_latency)
            self.results["latency_p50"].append(p50_latency)
            self.results["latency_p90"].append(p90_latency)
            self.results["latency_p99"].append(p99_latency)

    async def run_accuracy_benchmark(self, num_test_cases: int = 20):
        """
        Run accuracy benchmarks by inserting known data and measuring retrieval accuracy.
        
        Args:
            num_test_cases: Number of test cases for each index size
        """
        print("\nRunning accuracy benchmarks...")
        
        for size, memory in self.memories.items():
            print(f"Testing accuracy for index with {size} entries...")
            
            # Create ground truth test cases
            ground_truth = []
            for i in range(num_test_cases):
                # Create a distinct vector for reliable retrieval
                query_vector = np.random.rand(384).tolist()
                doc_id = f"accuracy_test_{i}"
                
                # Add small variation to create a nearby but not identical vector
                doc_vector = query_vector.copy()
                for j in range(len(doc_vector)):
                    doc_vector[j] += random.uniform(-0.01, 0.01)  # Small perturbation
                
                # Add the document to memory
                doc = {
                    "id": doc_id,
                    "content": f"Accuracy test document {i}",
                    "embedding": doc_vector,
                    "metadata": {"source": "accuracy_test"}
                }
                await memory.add(doc)
                ground_truth.append((query_vector, doc_id))
            
            # Test retrieval accuracy
            correct_retrievals = 0
            for query_vector, expected_id in tqdm(ground_truth, desc="Accuracy tests"):
                results = await memory.retrieve_design_memories(query_vector, top_k=5)
                # Check if the expected document is in the results
                retrieved_ids = [r.get("id") for r in results]
                if expected_id in retrieved_ids:
                    correct_retrievals += 1
            
            accuracy = correct_retrievals / num_test_cases
            print(f"Accuracy for {size} entries: {accuracy:.2%}")
            
            # Store results
            self.results["accuracy"].append(accuracy)

    def generate_report(self):
        """Generate a report with benchmark results and visualizations."""
        print("\nGenerating benchmark report...")
        
        # Convert results to DataFrame
        df = pd.DataFrame(self.results)
        
        # Print tabular results
        print("\nBenchmark Results:")
        print(df.to_string(index=False))
        
        # Save results to CSV
        df.to_csv("memory_retrieval_benchmark_results.csv", index=False)
        print("Results saved to memory_retrieval_benchmark_results.csv")
        
        # Generate visualizations
        self._generate_visualizations(df)
    
    def _generate_visualizations(self, df: pd.DataFrame):
        """
        Generate visualizations from benchmark results.
        
        Args:
            df: DataFrame with benchmark results
        """
        plt.figure(figsize=(12, 10))
        
        # Plot 1: Latency by index size
        plt.subplot(2, 1, 1)
        plt.plot(df["size"], df["latency_mean"], marker='o', label="Mean")
        plt.plot(df["size"], df["latency_p50"], marker='s', label="P50")
        plt.plot(df["size"], df["latency_p90"], marker='^', label="P90")
        plt.plot(df["size"], df["latency_p99"], marker='*', label="P99")
        
        plt.title("Memory Retrieval Latency by Index Size")
        plt.xlabel("Index Size (entries)")
        plt.ylabel("Latency (ms)")
        plt.xscale("log")
        plt.grid(True)
        plt.legend()
        
        # Plot 2: Accuracy by index size
        plt.subplot(2, 1, 2)
        plt.plot(df["size"], df["accuracy"], marker='o', color='green')
        plt.title("Memory Retrieval Accuracy by Index Size")
        plt.xlabel("Index Size (entries)")
        plt.ylabel("Accuracy")
        plt.xscale("log")
        plt.ylim(0, 1.05)
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig("memory_retrieval_benchmark.png")
        print("Visualization saved to memory_retrieval_benchmark.png")

async def main():
    """Main function to run the benchmark."""
    parser = argparse.ArgumentParser(description='Benchmark memory retrieval methods')
    parser.add_argument('--sizes', type=int, nargs='+', default=[1000, 10000, 100000],
                        help='Index sizes to benchmark (default: 1000 10000 100000)')
    parser.add_argument('--queries', type=int, default=50,
                        help='Number of queries for latency benchmark (default: 50)')
    parser.add_argument('--accuracy-tests', type=int, default=20,
                        help='Number of test cases for accuracy benchmark (default: 20)')
    
    args = parser.parse_args()
    
    # Run benchmark
    benchmark = MemoryRetrievalBenchmark(index_sizes=args.sizes)
    
    try:
        await benchmark.setup_indexes()
        await benchmark.run_latency_benchmark(num_queries=args.queries)
        await benchmark.run_accuracy_benchmark(num_test_cases=args.accuracy_tests)
        benchmark.generate_report()
    except Exception as e:
        print(f"Benchmark failed: {e}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
