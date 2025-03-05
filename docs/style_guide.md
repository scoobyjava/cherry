# Cherry Project Style Guide

This document outlines the coding style and naming conventions for the Cherry project to ensure consistency across all parts of the codebase.

## Configuration Files

### Naming Conventions

1. **Use snake_case for all keys and property names**
   - Correct: `api_key`, `connection_pool`, `max_size`
   - Incorrect: `apiKey`, `connectionPool`, `maxSize`

2. **Time Units**
   - Always use milliseconds as the base unit
   - Always include the `_ms` suffix for clarity: `timeout_ms`, `delay_ms`, `interval_ms`
   - For longer durations that are more readable in seconds or minutes, convert to ms: `60000` instead of `60` seconds

3. **Boolean Properties**
   - Use direct descriptive names without prefixes: `enabled`, `active`, `visible`
   - Avoid `is_` or `has_` prefixes: prefer `enabled` over `is_enabled`

4. **Structural Naming**
   - Group related settings under descriptive parent objects
   - Use consistent naming across similar components (e.g., `connection` has the same structure in different services)
   - Prefer `min_` and `max_` prefixes for range values

5. **Environment Variables**
   - Use uppercase with underscores: `${POSTGRES_HOST}`, `${OPENAI_API_KEY}`
   - Reference them consistently using `${VAR_NAME}` syntax

### Structure Conventions

1. **Common Sections**
   - Each service should have similar section organization:
     - Connection settings
     - Authentication
     - Performance settings
     - Monitoring
     - Backup/disaster recovery

2. **Nesting Depth**
   - Aim for maximum 4 levels of nesting
   - Group related settings under meaningful categories

## Implementation Guidelines

This style guide should be enforced through code reviews and automated linting tools. Any deviation should require explicit justification.
