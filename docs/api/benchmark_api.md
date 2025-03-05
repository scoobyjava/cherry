# Benchmark API Documentation

This document provides a detailed overview of the benchmark configuration API used by the Cherry application.

## Configuration Overview

The benchmark configuration controls settings for all benchmark services and components. It's stored in `benchmarks/benchmark_config.json`.

## Services Configuration

### Pinecone Vector Database

```json
"pinecone": {
  "index_name": "memory-benchmark",
  "default_top_k": 5,
  "namespaces": {
    // Namespace configurations
  }
}
```

- **index_name**: The name of the Pinecone index to use for vector storage
- **default_top_k**: Default number of results to return from queries
- **namespaces**: Specialized configuration for different vector use cases

#### Namespaces

Each namespace has specific metadata schemas for different agent types:

- **search_agent**: For search-related vectors
- **recommendation_agent**: For recommendation vectors
- **qa_agent**: For question-answering vectors

### PostgreSQL Database

```json
"postgres": {
  "database": "${POSTGRES_DB}",
  "query_settings": {
    "statement_timeout_ms": 30000
  }
}
```

- **database**: Database name (from environment variable)
- **query_settings.statement_timeout_ms**: Maximum query execution time in milliseconds

### OpenAI API

```json
"openai": {
  "default_model": "gpt-4",
  "max_tokens": 8192
}
```

- **default_model**: Default model to use if not specified
- **max_tokens**: Maximum response length

## Feature Flags

Configuration options to enable/disable specific benchmark components:

```json
"feature_flags": {
  "security_scanning": {
    "checkov": true,
    "dependency_scan": true
  },
  "profiling": {
    "enabled": true,
    "cpu_profiling": true,
    "memory_profiling": true
  }
}
```

## Validation Rules

Rules for validating configuration values:

```json
"validation": {
  "port_ranges": {
    "min": 1024,
    "max": 65535
  },
  "cron_expressions": {
    "validate_before_apply": true
  }
}
```

## Exception Handling

Configuration for error handling behaviors:

```json
"exception_handling": {
  "enabled": true,
  "log_level": "error",
  "metrics_collection": true,
  "alert_on_consecutive_failures": 3,
  "circuit_breaker": {
    // Circuit breaker pattern configuration
  }
}
```

### Circuit Breaker Pattern

```json
"circuit_breaker": {
  "enabled": true,
  "threshold_percentage": 50,
  "min_request_count": 20,
  "window_size_seconds": 60,
  "sleep_window_ms": 5000
}
```

## Usage Examples

### Configuring a New Pinecone Namespace

```json
"custom_agent": {
  "description": "Namespace for custom agent vectors",
  "metadata_schema": {
    "agent_id": "string",
    "context_type": "string",
    "confidence": "number",
    "timestamp": "number"
  },
  "default_top_k": 7
}
```

### Modifying Feature Flags

```json
"feature_flags": {
  "security_scanning": {
    "checkov": false,
    "dependency_scan": true
  },
  "profiling": {
    "enabled": true,
    "cpu_profiling": false,
    "memory_profiling": true
  }
}
```
