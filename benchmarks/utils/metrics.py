import time
import psutil
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Any


class MetricsCollector:
    """Collects system metrics during benchmark runs"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.cpu_percent_samples = []
        self.memory_samples = []
        self.io_counters_start = None
        self.io_counters_end = None

    def start_collection(self):
        """Start collecting metrics"""
        self.start_time = time.time()
        self.cpu_percent_samples = []
        self.memory_samples = []
        self.io_counters_start = psutil.net_io_counters()
        # Start CPU monitoring in a non-blocking way
        psutil.cpu_percent(interval=None)
        
    def sample(self):
        """Take a sample of current system metrics"""
        if self.start_time is None:
            raise RuntimeError("Must call start_collection() before sampling")
            
        self.cpu_percent_samples.append(psutil.cpu_percent(interval=None))
        self.memory_samples.append(psutil.virtual_memory().percent)
        
    def end_collection(self):
        """Stop collecting metrics and return results"""
        if self.start_time is None:
            raise RuntimeError("Must call start_collection() before end_collection()")
            
        self.end_time = time.time()
        self.io_counters_end = psutil.net_io_counters()
        
        # Take final samples if none were taken
        if not self.cpu_percent_samples:
            self.sample()
            
        duration = self.end_time - self.start_time
        
        # Calculate network I/O
        bytes_sent = self.io_counters_end.bytes_sent - self.io_counters_start.bytes_sent
        bytes_recv = self.io_counters_end.bytes_recv - self.io_counters_start.bytes_recv
        
        metrics = {
            "duration_seconds": duration,
            "cpu_percent": {
                "min": min(self.cpu_percent_samples) if self.cpu_percent_samples else 0,
                "max": max(self.cpu_percent_samples) if self.cpu_percent_samples else 0,
                "avg": statistics.mean(self.cpu_percent_samples) if self.cpu_percent_samples else 0,
            },
            "memory_percent": {
                "min": min(self.memory_samples) if self.memory_samples else 0,
                "max": max(self.memory_samples) if self.memory_samples else 0,
                "avg": statistics.mean(self.memory_samples) if self.memory_samples else 0,
            },
            "network": {
                "bytes_sent": bytes_sent,
                "bytes_received": bytes_recv,
                "send_rate_mbps": (bytes_sent / duration) / (1024 * 1024) if duration > 0 else 0,
                "receive_rate_mbps": (bytes_recv / duration) / (1024 * 1024) if duration > 0 else 0,
            }
        }
        
        # Reset for next collection
        self.start_time = None
        self.end_time = None
        
        return metrics


@dataclass
class BenchmarkResult:
    """Store benchmark results for a single test"""
    test_name: str
    system_name: str
    dataset_size: int
    latencies: List[float] = field(default_factory=list)
    
    @property
    def min_latency(self):
        return min(self.latencies) if self.latencies else 0
        
    @property
    def max_latency(self):
        return max(self.latencies) if self.latencies else 0
        
    @property
    def avg_latency(self):
        return statistics.mean(self.latencies) if self.latencies else 0
        
    @property
    def p95_latency(self):
        if not self.latencies:
            return 0
        sorted_latencies = sorted(self.latencies)
        idx = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[idx]
    
    def to_dict(self):
        return {
            "min": self.min_latency,
            "max": self.max_latency,
            "avg": self.avg_latency,
            "p95": self.p95_latency,
            "samples": len(self.latencies)
        }
