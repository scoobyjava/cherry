# Cherry API Documentation

This directory contains comprehensive documentation for Cherry's APIs and configuration interfaces.

## Available Documentation

- [Benchmark API Documentation](./benchmark_api.md) - Documentation for configuring and using the benchmark system

## Configuration Schemas

The following JSON schema files are available for validating configuration:

- `benchmarks/schema/benchmark_config_schema.json` - Schema for benchmark configuration

## Best Practices

When working with Cherry's configuration interfaces:

1. **Use schema validation** to ensure your configuration is valid
2. **Reference environment variables** for sensitive or deployment-specific values
3. **Use namespaces** appropriately to organize vector storage
4. **Review feature flags** to ensure only needed features are enabled
5. **Configure circuit breakers** to prevent cascading failures

## Examples

Example configurations can be found in the documentation files or in the `examples` directory.
