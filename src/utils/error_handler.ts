/**
 * Centralized error handling utility for the Cherry application
 * Provides consistent error types, formatting, and handling strategies
 */

import { v4 as uuidv4 } from 'uuid';
import config from '../../benchmarks/benchmark_config.json';

// Base error type with consistent properties
export class AppError extends Error {
  public readonly errorId: string;
  public readonly timestamp: number;
  public readonly originalError?: unknown;
  public readonly context?: Record<string, unknown>;
  
  constructor(message: string, options: {
    originalError?: unknown;
    context?: Record<string, unknown>;
  } = {}) {
    super(message);
    this.name = this.constructor.name;
    this.errorId = uuidv4();
    this.timestamp = Date.now();
    this.originalError = options.originalError;
    this.context = options.context;
    
    // Preserve stack trace
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }
  
  toJSON() {
    return {
      errorId: this.errorId,
      name: this.name,
      message: this.message,
      timestamp: this.timestamp,
      context: this.context,
      stack: this.stack,
      originalError: this.originalError instanceof Error 
        ? {
            name: this.originalError.name,
            message: this.originalError.message,
            stack: this.originalError.stack,
          }
        : this.originalError
    };
  }
}

// Service-specific errors
export class PineconeError extends AppError {
  constructor(message: string, options: {
    originalError?: unknown;
    context?: Record<string, unknown>;
    namespace?: string;
  } = {}) {
    super(`Pinecone Error: ${message}`, options);
    this.name = 'PineconeError';
  }
}

export class PostgresError extends AppError {
  public readonly queryTimeout: number;
  
  constructor(message: string, options: {
    originalError?: unknown;
    context?: Record<string, unknown>;
    queryId?: string;
  } = {}) {
    super(`Postgres Error: ${message}`, options);
    this.name = 'PostgresError';
    this.queryTimeout = config.app.services.postgres.query_settings.statement_timeout_ms;
  }
}

export class OpenAIError extends AppError {
  public readonly model: string;
  
  constructor(message: string, options: {
    originalError?: unknown;
    context?: Record<string, unknown>;
    model?: string;
  } = {}) {
    super(`OpenAI Error: ${message}`, options);
    this.name = 'OpenAIError';
    this.model = options.model || config.app.services.openai.default_model;
  }
}

// Error handling utilities
export function handleError(error: unknown, errorType: string): AppError {
  // Log the error
  console.error(`Error caught (${errorType}):`, error);
  
  if (error instanceof AppError) {
    return error;
  }
  
  // Convert unknown errors to AppError
  if (error instanceof Error) {
    return new AppError(error.message, { originalError: error });
  }
  
  // Handle non-Error types
  return new AppError(String(error), { originalError: error });
}

// Retry utilities
type RetryOptions = {
  maxRetries: number;
  initialDelay: number;
  maxDelay: number;
  factor: number;
  retryableErrors?: RegExp[];
};

// Default retry options based on service
const defaultRetryOptions: Record<string, RetryOptions> = {
  pinecone: {
    maxRetries: 5,
    initialDelay: 100,
    maxDelay: 5000,
    factor: 2,
    retryableErrors: [/timeout/i, /rate limit/i, /too many requests/i, /503/]
  },
  postgres: {
    maxRetries: 3,
    initialDelay: 200,
    maxDelay: 2000,
    factor: 2,
    retryableErrors: [/connection/i, /timeout/i, /deadlock/i, /serialization/i]
  },
  openai: {
    maxRetries: 3,
    initialDelay: 1000,
    maxDelay: 10000,
    factor: 2,
    retryableErrors: [/rate limit/i, /timeout/i, /server error/i, /503/]
  }
};

// Generic retry function with exponential backoff
export async function withRetry<T>(
  fn: () => Promise<T>,
  serviceName: keyof typeof defaultRetryOptions,
  customOptions?: Partial<RetryOptions>
): Promise<T> {
  const options = { ...defaultRetryOptions[serviceName], ...customOptions };
  let lastError: Error | undefined;
  
  for (let attempt = 0; attempt < options.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      
      // Check if error is retryable
      const isRetryable = !options.retryableErrors || 
        options.retryableErrors.some(pattern => pattern.test(lastError!.message));
      
      if (!isRetryable || attempt === options.maxRetries - 1) {
        throw error;
      }
      
      // Calculate delay with exponential backoff and jitter
      const delay = Math.min(
        options.initialDelay * Math.pow(options.factor, attempt) * (0.8 + Math.random() * 0.4),
        options.maxDelay
      );
      
      console.warn(`Retry attempt ${attempt + 1}/${options.maxRetries} after ${delay}ms delay`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  // This should never happen due to the throw in the loop
  throw lastError || new Error('Unknown error during retry');
}
