const { createConnectionConfig, createBackupConfig, createNamespaceConfig } = require('./config_templates');

/**
 * Generates the full benchmark configuration
 * @param {Object} env - Environment variables
 * @returns {Object} Complete benchmark configuration
 */
function generateBenchmarkConfig(env) {
  return {
    pinecone: {
      api_key: env.PINECONE_API_KEY,
      environment: "us-west1-gcp",
      index_name: "memory-benchmark",
      connection: createConnectionConfig('basic'),
      namespaces: {
        search_agent: createNamespaceConfig(
          "Namespace for search-related vectors",
          {
            source_type: "string",
            timestamp: "number",
            relevance_score: "number",
            category: "string"
          }
        ),
        recommendation_agent: createNamespaceConfig(
          "Namespace for recommendation vectors",
          {
            user_id: "string",
            item_id: "string",
            interaction_type: "string",
            timestamp: "number"
          },
          { vector_count_limit: 150000, default_top_k: 10 }
        ),
        qa_agent: createNamespaceConfig(
          "Namespace for question-answering vectors",
          {
            document_id: "string",
            section_id: "string",
            confidence: "number",
            last_updated: "number"
          },
          { vector_count_limit: 75000, default_top_k: 3, limit_handling: "evict_lowest_confidence" }
        )
      },
      backup: createBackupConfig({ retention_days: 7 }, "0 2 * * *", "/secure/backups/pinecone"),
      high_availability: {
        enabled: true,
        replica_zones: ["us-east1-gcp", "eu-west1-gcp"],
        failover: {
          auto_failover: true,
          max_failover_time_seconds: 60,
          health_check_interval_seconds: 30
        }
      }
    },
    postgres: {
      host: env.POSTGRES_HOST,
      port: 5432,
      database: env.POSTGRES_DB,
      user: env.POSTGRES_USER,
      password: env.POSTGRES_PASSWORD,
      connection: {
        timeout_seconds: 30,
        max_connections: 100,
        idle_timeout_seconds: 60,
        ssl_mode: "require"
      },
      backup: createBackupConfig(
        { 
          retention_days: 30, 
          compression: true,
          validation: {
            verify_integrity: true,
            alert_on_failure: true
          }
        }, 
        "0 1 * * *", 
        "/secure/backups/postgres"
      ),
      replication: {
        // Configuration for replication remains unchanged as it's specific to postgres
        enabled: true,
        mode: "streaming",
        replicas: [
          { host: "pg-replica-1", port: 5432, priority: 1 },
          { host: "pg-replica-2", port: 5432, priority: 2 }
        ],
        sync_commit: "on",
        max_lag_seconds: 30,
        automatic_failover: true,
        monitoring: {
          check_interval_seconds: 15,
          failover_threshold: 3,
          recovery_wait_seconds: 60
        }
      }
    },
    
    // Other service configurations would follow the same pattern...
  };
}

module.exports = { generateBenchmarkConfig };
