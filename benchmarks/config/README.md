# Benchmark Configuration System

This directory contains configuration files for the benchmark system.

## Configuration Files

- `defaults.json`: Default values for all configurable parameters 
- `benchmark_config.json`: Main configuration file that references default values

## Usage

The benchmark system uses a hierarchical configuration approach:

1. Hard-coded defaults (in `defaults.json`)
2. Environment variables
3. Command-line arguments (highest priority)

## Configuration Parameters

### Pinecone Service
- `DEFAULT_PINECONE_TOP_K`: Default number of results to return (default: 5)
- `DEFAULT_SEARCH_TOP_K`: Results for search agent (default: 5)
- `DEFAULT_RECOMMENDATION_TOP_K`: Results for recommendation agent (default: 10)
- `DEFAULT_QA_TOP_K`: Results for QA agent (default: 3)

### PostgreSQL Service
- `POSTGRES_QUERY_TIMEOUT`: Maximum query execution time in milliseconds (default: 30000)

### OpenAI Service
- `OPENAI_DEFAULT_MODEL`: Default model to use (default: "gpt-4")
- `OPENAI_MAX_TOKENS`: Maximum response length (default: 8192)

### Exception Handling
- `ALERT_CONSECUTIVE_FAILURES`: Number of failures before alerting (default: 3)
- `CIRCUIT_BREAKER_THRESHOLD`: Percentage of failures to trip breaker (default: 50)
- `CIRCUIT_BREAKER_MIN_REQUESTS`: Minimum requests before applying threshold (default: 20)
- `CIRCUIT_BREAKER_WINDOW`: Time window for failure evaluation in seconds (default: 60)
- `CIRCUIT_BREAKER_SLEEP`: Cooldown period after circuit opens in milliseconds (default: 5000)

### Validation
- `MIN_PORT`: Minimum non-privileged port (default: 1024)
- `MAX_PORT`: Maximum valid port number (default: 65535)
