# Improved Configuration Structure Example

This document provides an example of how the configuration could be restructured to address the architectural weaknesses.

## Layered Configuration Approach

```json
{
  "application": {
    "name": "cherry",
    "version": "1.0.0",
    "environment": "${ENVIRONMENT}",
    "log_level": "${LOG_LEVEL}"
  },
  
  "services": {
    "vector_db": {
      "provider": "pinecone",
      "config_ref": "integrations.pinecone",
      "features": {
        "search": true,
        "recommendations": true,
        "qa": true
      },
      "dependencies": ["logging", "monitoring"]
    },
    "relational_db": {
      "provider": "postgres",
      "config_ref": "integrations.postgres",
      "features": {
        "user_data": true,
        "analytics": true
      },
      "dependencies": ["logging", "monitoring"]
    },
    "ai_provider": {
      "provider": "openai",
      "config_ref": "integrations.openai",
      "dependencies": ["vector_db", "logging", "monitoring"]
    }
  },
  
  "integrations": {
    "pinecone": {
      "connection": {
        "api_key_ref": "secrets.pinecone_api_key",
        "environment": "${PINECONE_ENVIRONMENT}",
        "timeout_ms": 3000,
        "retry_policy_ref": "resilience.standard_retry"
      },
      "index": {
        "name": "${PINECONE_INDEX_NAME}",
        "namespaces": {
          "search_agent": {
            "metadata_schema_ref": "schemas.search_metadata"
          },
          "recommendation_agent": {
            "metadata_schema_ref": "schemas.recommendation_metadata"
          },
          "qa_agent": {
            "metadata_schema_ref": "schemas.qa_metadata"
          }
        }
      }
    },
    "postgres": {
      "connection": {
        "host": "${POSTGRES_HOST}",
        "port": "${POSTGRES_PORT:5432}",
        "database": "${POSTGRES_DB}",
        "credentials_ref": "secrets.postgres_credentials",
        "timeout_ms": 15000,
        "pooling_ref": "resilience.db_connection_pool"
      }
    },
    "openai": {
      "connection": {
        "api_key_ref": "secrets.openai_api_key",
        "organization_id": "${OPENAI_ORG_ID}",
        "timeout_ms": 30000,
        "retry_policy_ref": "resilience.ai_provider_retry"
      },
      "defaults": {
        "model": "gpt-4",
        "max_tokens": 8192
      }
    }
  },
  
  "resilience": {
    "standard_retry": {
      "max_attempts": 3,
      "backoff_ms": 1000,
      "exponential": true
    },
    "ai_provider_retry": {
      "max_attempts": 3,
      "backoff_ms": 2000,
      "exponential": true
    },
    "db_connection_pool": {
      "min_size": 10,
      "max_size": 100,
      "idle_timeout_ms": 60000
    }
  },
  
  "observability": {
    "logging": {
      "service": "cloudwatch",
      "config_ref": "integrations.cloudwatch",
      "levels": {
        "production": "warn",
        "staging": "info",
        "development": "debug"
      }
    },
    "monitoring": {
      "service": "prometheus",
      "config_ref": "integrations.prometheus",
      "metrics": {
        "request_duration_ms": true,
        "error_count": true,
        "active_connections": true
      },
      "alerts": {
        "latency_threshold_ms": 1000,
        "error_rate_threshold": 0.01,
        "notification_channels_ref": "notifications.channels"
      }
    },
    "tracing": {
      "service": "opentelemetry",
      "config_ref": "integrations.opentelemetry",
      "sampling_rate": 0.1
    }
  },
  
  "operations": {
    "backups": {
      "postgres": {
        "schedule": "0 1 * * *",
        "retention_days": 30,
        "storage_ref": "integrations.object_storage"
      },
      "pinecone": {
        "schedule": "0 2 * * *",
        "retention_days": 7,
        "storage_ref": "integrations.object_storage"
      }
    },
    "high_availability": {
      "postgres": {
        "replicas": 2,
        "automatic_failover": true
      },
      "pinecone": {
        "replica_zones": ["${REPLICA_ZONE_1}", "${REPLICA_ZONE_2}"]
      }
    }
  },
  
  "schemas": {
    "search_metadata": {
      "source_type": "string",
      "timestamp": "number",
      "relevance_score": "number",
      "category": "string"
    },
    "recommendation_metadata": {
      "user_id": "string",
      "item_id": "string",
      "interaction_type": "string",
      "timestamp": "number"
    },
    "qa_metadata": {
      "document_id": "string",
      "section_id": "string",
      "confidence": "number",
      "last_updated": "number"
    }
  },
  
  "secrets": {
    "provider": "vault",
    "config": {
      "address": "${VAULT_ADDR}",
      "auth_method": "kubernetes",
      "timeout_ms": 5000
    },
    "paths": {
      "pinecone_api_key": "secret/data/pinecone/api_key",
      "postgres_credentials": "secret/data/postgres/credentials",
      "openai_api_key": "secret/data/openai/api_key"
    }
  }
}
```

## Key Improvements

1. **Layered Structure**: Configuration is split into logical layers (application, services, integrations, etc.).

2. **Service Registry Pattern**: The `services` section explicitly defines services and their dependencies.

3. **Reference Pattern**: Uses `_ref` suffix to reference other parts of the configuration, creating a linked structure.

4. **Separation of Concerns**: 
   - Services define what capabilities are enabled
   - Integrations define how to connect to external services
   - Resilience defines retry and connection pooling strategies
   - Observability handles logging, monitoring, and tracing
   - Operations handles backups and high availability

5. **Schema Definitions**: Explicit schemas are defined and referenced.

6. **Infrastructure Independence**: All environment-specific values are externalized as environment variables.

7. **Centralization of Cross-Cutting Concerns**: Retry policies, connection pooling, and monitoring are defined once and referenced.

8. **Secrets Management**: Clear separation of secrets from configuration.

This structure promotes:
- Reusability through references
- Loose coupling through dependency injection
- Maintainability through standardization
- Flexibility through clean separation of concerns
