const fs = require('fs');
const path = require('path');

class ErrorHandler {
  constructor(configPath = '../error/exception_config.json') {
    try {
      const configFile = path.resolve(__dirname, configPath);
      this.config = JSON.parse(fs.readFileSync(configFile, 'utf8'));
    } catch (err) {
      console.error('Failed to load error configuration:', err);
      this.config = {
        error_codes: {},
        retry_policies: { default: { max_attempts: 3 } },
        logging: { error_levels: { error: 2 } }
      };
    }
    
    this.metrics = {
      errorCounts: {},
      retryAttempts: {}
    };
  }

  getErrorCode(service, errorType) {
    try {
      if (service in this.config.error_codes.service_errors && 
          errorType in this.config.error_codes.service_errors[service]) {
        return this.config.error_codes.service_errors[service][errorType];
      } else if (errorType in this.config.error_codes.application_errors) {
        return this.config.error_codes.application_errors[errorType];
      }
    } catch (err) {
      // Fallback for config errors
    }
    return 'UNKNOWN';
  }

  getRetryPolicy(service) {
    try {
      return this.config.retry_policies[service] || this.config.retry_policies.default;
    } catch (err) {
      return { max_attempts: 3, initial_backoff_ms: 100, backoff_multiplier: 2.0 };
    }
  }

  async executeWithRetry(service, operation, ...args) {
    const policy = this.getRetryPolicy(service);
    let attempts = 0;
    let backoffTime = policy.initial_backoff_ms;
    
    while (true) {
      attempts++;
      try {
        return await operation(...args);
      } catch (error) {
        // Track metrics
        this.metrics.retryAttempts[service] = (this.metrics.retryAttempts[service] || 0) + 1;
        
        const shouldRetry = attempts < policy.max_attempts && 
                           (this.isRetryableError(error, policy.retry_on_status_codes));
        
        if (!shouldRetry) {
          this.logError(service, error);
          throw error;
        }
        
        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, backoffTime));
        backoffTime = Math.min(backoffTime * policy.backoff_multiplier, policy.max_backoff_ms);
      }
    }
  }

  isRetryableError(error, retryCodes) {
    // Check if error has status code that matches retry codes
    if (error.status && retryCodes.includes(error.status)) return true;
    if (error.statusCode && retryCodes.includes(error.statusCode)) return true;
    if (error.code && retryCodes.includes(error.code)) return true;
    
    // Network errors are typically retryable
    return error.message && (
      error.message.includes('ECONNRESET') || 
      error.message.includes('ETIMEDOUT') ||
      error.message.includes('ECONNREFUSED')
    );
  }
  
  logError(service, error, level = 'error', metadata = {}) {
    const errorCode = this.getErrorCode(service, this.categorizeError(error));
    
    // Track error counts
    this.metrics.errorCounts[errorCode] = (this.metrics.errorCounts[errorCode] || 0) + 1;
    
    // Build error log object
    const logObject = {
      timestamp: new Date().toISOString(),
      service,
      error_code: errorCode,
      message: error.message || 'Unknown error',
      level
    };
    
    if (this.config.logging.includeStackTrace && error.stack) {
      logObject.stack_trace = error.stack;
    }
    
    if (this.config.logging.includeMetadata) {
      logObject.metadata = { ...metadata };
      
      if (error.code) logObject.metadata.code = error.code;
      if (error.status) logObject.metadata.status = error.status;
      if (error.statusCode) logObject.metadata.statusCode = error.statusCode;
    }
    
    // Log based on level
    switch (level) {
      case 'critical':
        console.error('[CRITICAL]', JSON.stringify(logObject));
        break;
      case 'error':
        console.error('[ERROR]', JSON.stringify(logObject));
        break;
      case 'warning':
        console.warn('[WARNING]', JSON.stringify(logObject));
        break;
      default:
        console.log(`[${level.toUpperCase()}]`, JSON.stringify(logObject));
    }
    
    return logObject;
  }
  
  categorizeError(error) {
    if (error.code === 'ECONNREFUSED' || error.message?.includes('connection')) {
      return 'connection_failure';
    } else if (error.code === 'ETIMEDOUT' || error.message?.includes('timeout')) {
      return 'query_timeout';
    } else if (error.status === 401 || error.statusCode === 401) {
      return 'authentication_error';
    } else if (error.status === 404 || error.statusCode === 404) {
      return 'resource_not_found';
    }
    
    return 'api_error';
  }
  
  getErrorMetrics() {
    return { ...this.metrics };
  }
  
  clearErrorMetrics() {
    this.metrics = {
      errorCounts: {},
      retryAttempts: {}
    };
  }
}

module.exports = ErrorHandler;
