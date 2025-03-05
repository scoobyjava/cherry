# Refactored Configuration Structure

This document demonstrates a configuration structure that better adheres to SOLID principles.

## Directory Structure

```
/config
├── manifest.json             # Main configuration that references other configs
├── services/
│   ├── vector_db/
│   │   ├── pinecone.json     # Concrete implementation
│   │   └── interface.json    # Interface definition
│   ├── relational_db/
│   │   ├── postgres.json     # Concrete implementation
│   │   └── interface.json    # Interface definition
│   └── ai_provider/
│       ├── openai.json       # Concrete implementation
│       └── interface.json    # Interface definition
├── features.json             # Feature flags configuration
└── validation.json           # Validation rules
```

## Example of abstracted vector database interface

```json
// services/vector_db/interface.json
{
  "version": "1.0",
  "interface": "vector_db",
  "required_methods": [
    "store_vectors",
    "query_vectors",
    "delete_vectors",
    "list_namespaces"
  ],
  "required_properties": [
    "namespaces",
    "default_top_k"
  ]
}
```

## Example of concrete implementation

```json
// services/vector_db/pinecone.json
{
  "implements": "vector_db",
  "version": "1.0",
  "implementation": "pinecone",
  "index_name": "memory-benchmark",
  "default_top_k": 5,
  "namespaces": {
    "search_agent": {
      "description": "Namespace for search-related vectors",
      "metadata_schema": {
        "source_type": "string",
        "timestamp": "number",
        "relevance_score": "number",
        "category": "string"
      },
      "default_top_k": 5
    },
    // Other namespaces...
  }
}
```

## Main manifest example

```json
// manifest.json
{
  "version": "1.0",
  "services": {
    "vector_db": {
      "implementation": "pinecone",
      "config_path": "services/vector_db/pinecone.json"
    },
    "relational_db": {
      "implementation": "postgres",
      "config_path": "services/relational_db/postgres.json"
    },
    "ai_provider": {
      "implementation": "openai",
      "config_path": "services/ai_provider/openai.json"
    }
  },
  "features_config_path": "features.json",
  "validation_config_path": "validation.json"
}
```

This structure allows:
- Single Responsibility: Each configuration file handles one concern
- Open/Closed: New implementations can be added without modifying existing ones
- Liskov Substitution: Implementations adhere to defined interfaces
- Interface Segregation: Clients only need to interact with relevant configuration parts
- Dependency Inversion: Code can depend on abstractions, not concrete implementations
