# Exception Handling System

This directory contains the error handling patterns and configurations for the Cherry application.

## Key Components

1. **exception_config.json**: Defines standardized error codes, retry policies, and logging settings
2. **error_handler.js**: Implements the central error handling logic with retry mechanisms

## Error Codes

Error codes follow a consistent pattern:
- Service-specific codes: `{SERVICE_PREFIX}-E{NUMBER}`
  - PCN: Pinecone
  - PG: PostgreSQL
  - OAI: OpenAI
- Application-wide codes: `APP-E{NUMBER}`

## Usage Examples

```javascript
const ErrorHandler = require('./error_handler');
const errorHandler = new ErrorHandler();

// Example 1: Execute with retry
async function queryPinecone(query) {
  return errorHandler.executeWithRetry('pinecone', async () => {
    // Your pinecone query code here
    const result = await pineconeClient.query(query);
    return result;
  });
}

// Example 2: Manual error handling
try {
  const result = await someOperation();
} catch (error) {
  const loggedError = errorHandler.logError('postgres', error, 'critical', {
    query: 'SELECT * FROM users',
    userId: 123
  });
  
  // Handle the error appropriately
  throw new Error(`Database operation failed: ${loggedError.error_code}`);
}

// Example 3: Get error metrics
const metrics = errorHandler.getErrorMetrics();
console.log(`Total Pinecone retries: ${metrics.retryAttempts.pinecone || 0}`);
```

## Retry Policies

Each service has customized retry policies with:
- Maximum retry attempts
- Initial backoff time
- Backoff multiplier (for exponential backoff)
- Maximum backoff time
- Status codes that trigger retries

## Best Practices

1. Always use the error handler for consistent error handling
2. Include relevant metadata when logging errors
3. Use appropriate error levels (critical, error, warning, info, debug)
4. Monitor error metrics to identify recurring issues
5. Implement circuit breakers for dependent services
