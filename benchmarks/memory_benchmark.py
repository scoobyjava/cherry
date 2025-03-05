#!/usr/bin/env python3

import argparse
import json
import time
import os
from datetime import datetime

# Local imports
from utils.config import load_config
from utils.metrics import MetricsCollector
from data_generators.vector_generator import VectorGenerator
from runners.pinecone_runner import PineconeRunner
from runners.postgres_runner import PostgresRunner

def parse_args():
    parser = argparse.ArgumentParser(description="Memory retrieval benchmark tool")
    parser.add_argument("--sizes", type=str, default="1k,10k,100k", 
                        help="Comma-separated list of dataset sizes to test")
    parser.add_argument("--query-counts", type=str, default="100,500,1000",
                        help="Comma-separated list of query counts to run")
    parser.add_argument("--dimensions", type=int, default=384,
                        help="Vector dimensions")
    parser.add_argument("--output", type=str, default="benchmark_results",
                        help="Output directory for results")
    parser.add_argument("--systems", type=str, default="pinecone,postgres",
                        choices=["pinecone", "postgres", "pinecone,postgres"],
                        help="Systems to benchmark")
    return parser.parse_args()

def size_to_int(size_str):
    """Convert size string like '1k' to integer"""
    if size_str.endswith('k'):
        return int(size_str[:-1]) * 1000
    elif size_str.endswith('m'):
        return int(size_str[:-1]) * 1000000
    return int(size_str)

def run_benchmark(config, args):
    # Initialize metrics collector
    metrics = MetricsCollector()
    
    # Parse sizes and queries
    sizes = [size_to_int(s.strip()) for s in args.sizes.split(",")]
    query_counts = [int(q.strip()) for q in args.query_counts.split(",")]
    systems = args.systems.split(",")
    
    # Initialize runners
    runners = {}
    if "pinecone" in systems:
        runners["pinecone"] = PineconeRunner(config["pinecone"])
    if "postgres" in systems:
        runners["postgres"] = PostgresRunner(config["postgres"])
    
    # Initialize vector generator
    vector_gen = VectorGenerator(args.dimensions)
    
    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    results = {}
    
    # Run benchmarks for each size
    for size in sizes:
        print(f"\n--- Running benchmarks for {size} vectors ---")
        results[size] = {}
        
        # Generate dataset
        print(f"Generating {size} test vectors...")
        dataset = vector_gen.generate_dataset(size)
        
        for system, runner in runners.items():
            print(f"Benchmarking {system}...")
            results[size][system] = {}
            
            # Insert data
            print(f"  Inserting {size} vectors...")
            insert_start = time.time()
            runner.insert_vectors(dataset)
            insert_time = time.time() - insert_start
            results[size][system]["insert_time"] = insert_time
            print(f"  Insert completed in {insert_time:.2f} seconds")
            
            # Run queries
            for query_count in query_counts:
                print(f"  Running {query_count} queries...")
                query_vectors = vector_gen.generate_query_vectors(query_count)
                
                # Simple search
                metrics.start_collection()
                search_results = runner.benchmark_search(query_vectors)
                metrics_data = metrics.end_collection()
                
                results[size][system][f"search_{query_count}"] = {
                    "latency": search_results,
                    "resource_usage": metrics_data
                }
                
                # Filtered search
                metrics.start_collection()
                filtered_results = runner.benchmark_filtered_search(query_vectors)
                metrics_data = metrics.end_collection()
                
                results[size][system][f"filtered_search_{query_count}"] = {
                    "latency": filtered_results,
                    "resource_usage": metrics_data
                }
            
            # Clean up
            runner.cleanup()
    
    # Save results
    result_file = os.path.join(args.output, f"benchmark_results_{timestamp}.json")
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nBenchmark completed. Results saved to {result_file}")
    
    # Print summary
    print("\n=== BENCHMARK SUMMARY ===")
    for size in sizes:
        print(f"\nDataset Size: {size} vectors")
        for system in systems:
            print(f"  {system.capitalize()}:")
            print(f"    Insert time: {results[size][system]['insert_time']:.2f}s")
            for query_count in query_counts:
                avg_latency = results[size][system][f"search_{query_count}"]["latency"]["avg"]
                print(f"    Avg search latency ({query_count} queries): {avg_latency:.4f}s")

if __name__ == "__main__":
    args = parse_args()
    config = load_config()
    run_benchmark(config, args)
``` 
