/**
 * Type definitions for benchmark configuration
 * @packageDocumentation
 */

/**
 * Root configuration object for benchmark application
 */
export interface BenchmarkConfig {
  /**
   * Main application configuration
   * Controls settings for all benchmark services, components, and behaviors
   */
  app: AppConfig;
}

/**
 * Application configuration
 */
export interface AppConfig {
  /**
   * Configuration for external services used during benchmarks
   * Includes vector databases, relational databases, and AI services
   */
  services: ServicesConfig;

  /**
   * Feature flags for enabling/disabling benchmark components
   * Use these to control which features are active during tests
   */
  featureFlags: FeatureFlags;

  /**
   * Validation rules for configuration values
   * Ensures that provided settings are within acceptable ranges
   */
  validation: ValidationConfig;

  /**
   * Error handling configuration
   * Controls how the application responds to failures during benchmarks
   */
  exceptionHandling: ExceptionHandlingConfig;
}

/**
 * External services configuration
 */
export interface ServicesConfig {
  /**
   * Pinecone vector database configuration for memory benchmarks
   * Used for storing and retrieving embeddings for various agent types
   */
  pinecone: PineconeConfig;

  /**
   * PostgreSQL database configuration
   * Used for storing structured benchmark data and results
   */
  postgres: PostgresConfig;

  /**
   * OpenAI API configuration
   * Controls model selection and response parameters
   */
  openai: OpenAIConfig;
}

/**
 * Pinecone vector database configuration
 */
export interface PineconeConfig {
  /**
   * Name of the Pinecone index to use for vector operations
   */
  index_name: string;

  /**
   * Default number of results to return from vector queries
   */
  default_top_k: number;

  /**
   * Configuration for different vector namespaces
   * Each namespace represents a different use case or data partition
   */
  namespaces: Record<string, NamespaceConfig>;
}

/**
 * Configuration for a Pinecone namespace
 */
export interface NamespaceConfig {
  /**
   * Description of the namespace purpose
   */
  description: string;

  /**
   * Schema definition for metadata fields attached to vectors
   */
  metadata_schema: Record<string, string>;

  /**
   * Number of results to return from queries in this namespace
   * Overrides the default_top_k setting from parent config
   */
  default_top_k: number;
}

/**
 * PostgreSQL database configuration
 */
export interface PostgresConfig {
  /**
   * Database name (supports environment variable references)
   */
  database: string;

  /**
   * Settings for query execution
   */
  query_settings: {
    /**
     * Maximum query execution time in milliseconds
     */
    statement_timeout_ms: number;
  };
}

/**
 * OpenAI API configuration
 */
export interface OpenAIConfig {
  /**
   * Default model to use if not explicitly specified
   */
  default_model: string;

  /**
   * Maximum response length
   */
  max_tokens: number;
}

/**
 * Feature flags configuration
 */
export interface FeatureFlags {
  /**
   * Security scanning features
   */
  security_scanning: {
    /**
     * Enable infrastructure-as-code security scanning
     */
    checkov: boolean;

    /**
     * Enable dependency vulnerability scanning
     */
    dependency_scan: boolean;
  };

  /**
   * Performance profiling features
   */
  profiling: {
    /**
     * Master switch for all profiling
     */
    enabled: boolean;

    /**
     * Track CPU usage during benchmarks
     */
    cpu_profiling: boolean;

    /**
     * Track memory consumption during benchmarks
     */
    memory_profiling: boolean;
  };
}

/**
 * Validation configuration
 */
export interface ValidationConfig {
  /**
   * Valid port number ranges
   */
  port_ranges: {
    /**
     * Minimum non-privileged port
     */
    min: number;

    /**
     * Maximum valid port number
     */
    max: number;
  };

  /**
   * Cron expression validation settings
   */
  cron_expressions: {
    /**
     * Whether to validate cron syntax before scheduling
     */
    validate_before_apply: boolean;
  };
}

/**
 * Exception handling configuration
 */
export interface ExceptionHandlingConfig {
  /**
   * Master switch for exception handling features
   */
  enabled: boolean;

  /**
   * Minimum level for logging exceptions
   */
  log_level: 'debug' | 'info' | 'warn' | 'error' | 'fatal';

  /**
   * Whether to collect metrics about exceptions
   */
  metrics_collection: boolean;

  /**
   * Number of consecutive failures before sending an alert
   */
  alert_on_consecutive_failures: number;

  /**
   * Circuit breaker pattern implementation
   * Prevents cascading failures by stopping requests after error threshold
   */
  circuit_breaker: {
    /**
     * Enable circuit breaker pattern
     */
    enabled: boolean;

    /**
     * Percentage of failures to trip breaker
     */
    threshold_percentage: number;

    /**
     * Minimum requests before applying threshold
     */
    min_request_count: number;

    /**
     * Time window for failure evaluation in seconds
     */
    window_size_seconds: number;

    /**
     * Cooldown period after circuit opens in milliseconds
     */
    sleep_window_ms: number;
  };
}
