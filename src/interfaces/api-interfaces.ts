/**
 * Core interfaces for the Cherry API
 * These define the contract between the API and its consumers
 */

/**
 * Configuration for vector database queries
 */
export interface VectorQueryOptions {
  /**
   * The namespace to query within the vector database
   * Must match one of the configured namespaces in the benchmark configuration
   */
  namespace: string;

  /**
   * Maximum number of results to return
   * @default Uses the namespace's default_top_k or falls back to service default
   */
  topK?: number;

  /**
   * Filter to apply to vector search based on metadata
   * Syntax depends on the underlying vector database implementation
   * @example "category:documentation AND timestamp>1648756800"
   */
  filter?: string;

  /**
   * Whether to include vector values in the response
   * @default false - Vectors are usually omitted to reduce response size
   */
  includeVectors?: boolean;
}

/**
 * Result from a vector database query
 */
export interface VectorQueryResult<T = Record<string, any>> {
  /**
   * Unique identifier of the vector
   */
  id: string;

  /**
   * Similarity score between query and result
   * Higher values indicate greater similarity
   * @range 0.0 to 1.0
   */
  score: number;

  /**
   * Vector values if requested in query options
   * Only included when includeVectors is true
   */
  vector?: number[];

  /**
   * Metadata associated with the vector
   * Schema depends on the namespace configuration
   */
  metadata: T;
}

/**
 * Response returned by vector query endpoints
 */
export interface VectorQueryResponse<T = Record<string, any>> {
  /**
   * The namespace that was queried
   */
  namespace: string;

  /**
   * Array of matching vector results
   */
  results: VectorQueryResult<T>[];

  /**
   * Total number of results returned
   */
  count: number;

  /**
   * Execution time in milliseconds
   */
  executionTimeMs: number;
}

/**
 * Error response format
 */
export interface ApiError {
  /**
   * Error code for machine-readable identification
   */
  code: string;

  /**
   * Human-readable error message
   */
  message: string;

  /**
   * Optional details about the error
   */
  details?: Record<string, any>;

  /**
   * Request ID for tracking errors through logs
   */
  requestId: string;
}

/**
 * Parameters for benchmark execution
 */
export interface BenchmarkRequest {
  /**
   * Type of benchmark to run
   * @example "memory", "latency", "throughput"
   */
  benchmarkType: string;

  /**
   * Configuration overrides for this benchmark run
   * Any values specified here will override the defaults in benchmark_config.json
   */
  configOverrides?: Record<string, any>;

  /**
   * Whether to run in verbose mode with additional logging
   * @default false
   */
  verbose?: boolean;
}
