# API Documentation Standards

## Overview

This document outlines the standards for documenting APIs within the Cherry project. Clear, consistent documentation improves developer experience and reduces integration time.

## General Principles

- **Completeness**: Document all endpoints, parameters, and response formats
- **Consistency**: Use consistent terminology and structure
- **Examples**: Provide usage examples for all endpoints
- **Error Handling**: Document all possible error codes and responses

## Documentation Format

### Endpoint Documentation

Each API endpoint should be documented with:

1. **HTTP Method and Path**: Clearly state the method (GET, POST, etc.) and URL path
2. **Description**: A concise explanation of the endpoint's purpose
3. **Request Parameters**: All parameters with:
   - Name
   - Type
   - Whether required or optional
   - Description
   - Constraints (if any)
4. **Request Body**: Schema and example
5. **Response**: Schema, status codes, and examples
6. **Error Responses**: Common error codes, messages, and troubleshooting guidance

## Example

```typescript
/**
 * Retrieves vector embeddings for a specified namespace
 * 
 * @route GET /api/vectors/{namespace}
 * 
 * @param {string} namespace - The vector namespace to query (required)
 * @param {number} topK - Number of results to return (optional, default: from namespace config)
 * @param {string} filter - Metadata filter expression (optional)
 * 
 * @returns {Object} 200 - Vector query results
 * @returns {Error} 400 - Invalid namespace or parameters
 * @returns {Error} 404 - Namespace not found
 * @returns {Error} 500 - Server error
 * 
 * @example
 * // Request
 * GET /api/vectors/search_agent?topK=3&filter=category:documentation
 * 
 * // Response (200 OK)
 * {
 *   "results": [
 *     {
 *       "id": "vec1",
 *       "score": 0.87,
 *       "metadata": {
 *         "source_type": "markdown",
 *         "category": "documentation",
 *         "timestamp": 1648756800
 *       }
 *     },
 *     ...
 *   ],
 *   "namespace": "search_agent",
 *   "count": 3
 * }
 */
```

## Tools and Automation

- Use JSDoc for inline documentation
- Generate API reference with TypeDoc
- Maintain OpenAPI specifications
- Run documentation validation in CI pipeline

## Review Process

All API changes must include corresponding documentation updates. Documentation PRs should include:

1. Updated endpoint documentation
2. Example requests/responses
3. Updated OpenAPI specs

## Interface Clarity Checklist

- [ ] Consistent naming conventions
- [ ] Logical parameter grouping
- [ ] Clear error communication
- [ ] Appropriate HTTP status codes
- [ ] Useful response structures
- [ ] Comprehensive example coverage
