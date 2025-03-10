"""
Module for tracking runtime performance metrics of Cherry-generated code.

This module provides functions to record performance metrics and automatically
identify performance issues when observed values deviate from desired benchmarks.

Functions:
    record_performance(metric_name: str, value: float) -> None:
        Records a performance metric value.
    identify_performance_issues(thresholds: Dict[str, float]) -> List[str]:
        Checks recorded metrics against provided thresholds and returns a list
        of issues that exceed defined limits.

Example scenario:
    # Record a slow query response time
    record_performance("response_time", 3.5)
    # Set a threshold for response time as 2.0 seconds
    issues = identify_performance_issues({"response_time": 2.0, "memory_usage": 100.0})
    if issues:
        # Trigger an optimization task (e.g., log the issue or schedule an optimization)
        print("Performance issues detected:")
        for issue in issues:
            print("-", issue)
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Global store for performance metrics.
# Each metric maps to the most recent recorded value.
performance_metrics: Dict[str, float] = {}


def record_performance(metric_name: str, value: float) -> None:
    """
    Record a performance metric.

    Args:
        metric_name: Name of the metric (e.g., 'response_time', 'memory_usage').
        value: Observed value of the metric.

    This function updates the global performance_metrics store with the latest value.
    """
    performance_metrics[metric_name] = value
    logger.info(f"Recorded performance metric '{metric_name}': {value}")


def identify_performance_issues(thresholds: Dict[str, float]) -> List[str]:
    """
    Identify performance issues by comparing recorded metrics against thresholds.

    Args:
        thresholds: A dictionary mapping metric names to threshold values. If the
                    recorded value of a metric exceeds the threshold, it is flagged.

    Returns:
        A list of issue messages describing which metrics exceeded their thresholds.
    """
    issues = []
    for metric, threshold in thresholds.items():
        measured = performance_metrics.get(metric)
        if measured is not None:
            # If the metric is a "response_time" (or similar), higher is worse.
            if measured > threshold:
                issues.append(
                    f"{metric} is {measured}, exceeds threshold of {threshold}")
                logger.info(
                    f"Metric '{metric}' issue detected: {measured} > {threshold}")
        else:
            logger.warning(f"No recorded value for metric '{metric}'")
    return issues


if __name__ == "__main__":
    import time

    # Example scenario: Cherry identifies a slow-performing query.
    logger.info("Simulating performance monitoring scenario...")

    # Simulate recording of performance metrics.
    # For instance, a slow query takes 3.5 seconds to complete.
    record_performance("response_time", 3.5)
    # Also record memory usage in MB
    record_performance("memory_usage", 85.0)
    # And CPU load in percentage
    record_performance("cpu_load", 72.0)

    # Define benchmarks / thresholds for acceptable performance.
    thresholds = {
        "response_time": 2.0,  # seconds
        "memory_usage": 100.0,  # MB
        "cpu_load": 80.0       # percent
    }

    issues = identify_performance_issues(thresholds)
    if issues:
        print("\nPerformance issues detected:")
        for issue in issues:
            print("-", issue)
        # Example: Automatically generate an optimization task.
        print("\nGenerating optimization task for slow-performing query...")
        # (In a real scenario, task generation could integrate with the TaskScheduler.)
    else:
        print("\nAll performance metrics are within acceptable thresholds.")
