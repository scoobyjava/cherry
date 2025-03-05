# Vector Database Memory Retrieval Benchmark

This benchmark compares the performance of Pinecone and PostgreSQL (with pgvector) for vector similarity search operations with increasing dataset sizes.

## Features

- Tests with multiple dataset sizes (1K, 10K, 100K vectors)
- Measures query latency (average, p95, p99)
- Monitors resource usage (CPU and memory)
- Generates detailed reports and visualizations

## Prerequisites

- Python 3.7+
- Pinecone account with API key
- PostgreSQL database with pgvector extension installed

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure the benchmark by editing `benchmark_config.json`:

```json
{
    "pinecone": {
        "api_key": "your-pinecone-api-key",
        "environment": "your-environment",
        "index_name": "memory-benchmark"
    },
    "postgres": {
        "host": "localhost",
        "port": 5432,
        "database": "vector_db",
        "user": "postgres",
        "password": "your-password"
    }
}
```

## Usage

Run the benchmark with:

```bash
# Load the configuration
cherry benchmark --config /workspaces/cherry/benchmarks/benchmark_config.json

# Test specific components
cherry benchmark pinecone --config /workspaces/cherry/benchmarks/benchmark_config.json
```

## Configuration Validation
Before running any benchmarks, validate your configuration:

```bash
cherry validate-config /workspaces/cherry/benchmarks/benchmark_config.json
```

# Benchmark Configuration Guide

## Overview
This document explains the benchmark configuration structure and best practices to avoid the previously identified issues.

## Key Improvements

### Secret Management
- Simplified secret syntax to work directly with the secret provider
- Added explicit secret management configuration section
- Removed mixed patterns (`:env_var`, `:file`) in favor of explicit configuration

### Connection Management
- Added timeout settings for all external services
- Added retry configurations for resilience
- Added proper SSL configurations for database connections

### High Availability
- Configured proper failover mechanisms with monitoring parameters
- Added health check intervals and thresholds
- Specified recovery waiting periods

### Data Management
- Added vector limit handling strategies
- Enhanced backup validation procedures
- Added secure paths for backups and credentials

### Security Enhancements
- Moved credentials to secure locations
- Added validation for configuration values
- Implemented rate limiting for API services