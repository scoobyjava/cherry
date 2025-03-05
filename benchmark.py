import time
import requests
from bs4 import BeautifulSoup
import argparse
import sys
import tracemalloc

# Benchmark scraping performance: speed, accuracy, and reliability.
def benchmark_scraping(url, iterations=5):
    total_time = 0
    successes = 0
    failures = 0
    expected_count = 10  # Expected minimum <p> tags for accuracy example
    for i in range(iterations):
        start = time.time()
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            count = len(soup.find_all('p'))
            if count >= expected_count:
                successes += 1
            else:
                failures += 1
        except Exception as e:
            print(f"Iteration {i+1} failed: {e}", file=sys.stderr)
            failures += 1
        elapsed = time.time() - start
        total_time += elapsed
        print(f"Iteration {i+1}: {elapsed:.3f}s, <p> count: {count if 'count' in locals() else 'N/A'}")
    avg_time = total_time / iterations
    print(f"\nAverage scraping time: {avg_time:.3f}s")
    print(f"Accuracy: {successes}/{iterations} iterations meeting expected count")
    print(f"Failures: {failures}/{iterations}")

# Benchmark memory storage/retrieval latency using tracemalloc.
def benchmark_memory_storage(data, retrieval_func, iterations=5):
    tracemalloc.start()
    times = []
    for i in range(iterations):
        start = time.time()
        retrieval_func(data)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"Memory retrieval iteration {i+1}: {elapsed:.6f}s")
    avg_time = sum(times) / iterations
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    print(f"\nAverage memory retrieval time: {avg_time:.6f}s")
    print("Top memory allocation lines:")
    for stat in top_stats[:3]:
        print(stat)
    tracemalloc.stop()

# Sample retrieval function to simulate memory data access.
def sample_storage_retrieval(data):
    # Simulated retrieval from a data structure.
    return data.get("content", None)

def main():
    parser = argparse.ArgumentParser(description="Benchmark scraping and memory storage retrieval performance.")
    parser.add_argument('--url', type=str, required=True, help='URL to benchmark scraping')
    parser.add_argument('--iterations', type=int, default=5, help='Number of iterations for benchmarks')
    args = parser.parse_args()
    
    print("Running scraping benchmark...")
    benchmark_scraping(args.url, args.iterations)

    print("\nRunning memory storage benchmark...")
    # Simulate data storage with sizable content for memory testing.
    data = {"content": " " * 1000000}  # 1 MB of blank space
    benchmark_memory_storage(data, sample_storage_retrieval, args.iterations)

if __name__ == '__main__':
    main()
