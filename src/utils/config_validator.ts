import { BenchmarkConfig } from '../types/benchmark_config';

/**
 * Validates a benchmark configuration object
 * @param config The configuration to validate
 * @returns An object containing validation results
 */
export function validateConfig(config: BenchmarkConfig): ValidationResult {
  const errors: ValidationError[] = [];
  
  // Validate Pinecone configuration
  if (!config.app?.services?.pinecone?.index_name) {
    errors.push({
      path: 'app.services.pinecone.index_name',
      message: 'Pinecone index name is required'
    });
  }
  
  // Validate OpenAI configuration
  if (config.app?.services?.openai?.max_tokens > 16384) {
    errors.push({
      path: 'app.services.openai.max_tokens',
      message: 'OpenAI max_tokens exceeds maximum allowed value (16384)'
    });
  }
  
  // Validate port ranges
  const { min, max } = config.app?.validation?.port_ranges || {};
  if (min !== undefined && max !== undefined) {
    if (min < 0 || min > 65535) {
      errors.push({
        path: 'app.validation.port_ranges.min',
        message: 'Port number must be between 0 and 65535'
      });
    }
    
    if (max < 0 || max > 65535) {
      errors.push({
        path: 'app.validation.port_ranges.max',
        message: 'Port number must be between 0 and 65535'
      });
    }
    
    if (min > max) {
      errors.push({
        path: 'app.validation.port_ranges',
        message: 'Minimum port cannot be greater than maximum port'
      });
    }
  }

  // Validate circuit breaker settings
  const cb = config.app?.exceptionHandling?.circuit_breaker;
  if (cb?.enabled) {
    if (cb.threshold_percentage < 0 || cb.threshold_percentage > 100) {
      errors.push({
        path: 'app.exceptionHandling.circuit_breaker.threshold_percentage',
        message: 'Threshold percentage must be between 0 and 100'
      });
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Result of a configuration validation
 */
export interface ValidationResult {
  /** Whether the configuration is valid */
  isValid: boolean;
  
  /** List of validation errors if any */
  errors: ValidationError[];
}

/**
 * Represents a single validation error
 */
export interface ValidationError {
  /** Path to the invalid property using dot notation */
  path: string;
  
  /** Description of the validation error */
  message: string;
}
