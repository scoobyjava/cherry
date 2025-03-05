import json
import os
import time
from typing import Dict, Any, Optional
import logging
import pinecone
import psycopg2
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config() -> Dict[str, Any]:
    """Load the benchmark configuration from the JSON file."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              "benchmarks", "benchmark_config.json")
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

def resolve_secret(value: str) -> str:
    """Resolve secret placeholders in the configuration."""
    if not isinstance(value, str):
        return value
        
    if value.startswith("${SECRET:") and value.endswith("}"):
        secret_name = value[9:-1].split(":")[0]
        # In a real implementation, this would retrieve from a secure secret store
        # For this example, we'll just check environment variables
        return os.environ.get(secret_name, "")
    return value

def get_db_connection(config: Dict[str, Any]):
    """Create a connection to the PostgreSQL database."""
    pg_config = config.get('postgres', {})
    
    try:
        return psycopg2.connect(
            host=resolve_secret(pg_config.get('host')),
            port=pg_config.get('port', 5432),
            database=resolve_secret(pg_config.get('database')),
            user=resolve_secret(pg_config.get('user')),
            password=resolve_secret(pg_config.get('password'))
        )
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def initialize_pinecone(config: Dict[str, Any]):
    """Initialize the Pinecone client."""
    pinecone_config = config.get('pinecone', {})
    
    try:
        pinecone.init(
            api_key=resolve_secret(pinecone_config.get('api_key')),
            environment=pinecone_config.get('environment')
        )
        return pinecone.Index(pinecone_config.get('index_name'))
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone: {e}")
        raise

def generate_embedding(text: str, config: Dict[str, Any]) -> list:
    """Generate an embedding for the given text using OpenAI's API."""
    openai_config = config.get('openai', {})
    openai.api_key = resolve_secret(openai_config.get('api_key'))
    
    try:
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"  # Using a standard embedding model
        )
        return response['data'][0]['embedding']
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        raise

def validate_agents(config: Dict[str, Any], source_agent: str, target_agent: str) -> bool:
    """Validate that both source and target agents exist in the Pinecone configuration."""
    pinecone_config = config.get('pinecone', {})
    namespaces = pinecone_config.get('namespaces', {})
    
    if source_agent not in namespaces:
        logger.error(f"Source agent '{source_agent}' not found in configuration")
        return False
        
    if target_agent not in namespaces:
        logger.error(f"Target agent '{target_agent}' not found in configuration")
        return False
        
    return True

def share_memory_between_agents(source_agent: str, target_agent: str, content: str, 
                              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Share memory from source agent to target agent.
    
    Args:
        source_agent: The name of the agent sharing the memory
        target_agent: The name of the agent receiving the memory
        content: The memory content to be shared
        metadata: Additional metadata for the memory (optional)
    
    Returns:
        Dict containing status and references to the stored memory
    """
    try:
        # Load configuration
        config = load_config()
        
        # Validate agents exist in configuration
        if not validate_agents(config, source_agent, target_agent):
            return {"success": False, "error": "Invalid agent names"}
        
        # Prepare metadata
        current_timestamp = int(time.time())
        memory_metadata = metadata or {}
        memory_metadata.update({
            "source_agent": source_agent,
            "timestamp": current_timestamp,
            "shared": True
        })
        
        # Adjust metadata based on target namespace schema
        pinecone_config = config.get('pinecone', {})
        target_namespace = pinecone_config.get('namespaces', {}).get(target_agent, {})
        schema = target_namespace.get('metadata_schema', {})
        
        # Filter metadata to match the target schema
        filtered_metadata = {k: v for k, v in memory_metadata.items() if k in schema}
        
        # Generate memory ID
        memory_id = f"{source_agent}_to_{target_agent}_{current_timestamp}"
        
        # Store in PostgreSQL
        conn = get_db_connection(config)
        cursor = conn.cursor()
        
        try:
            # Create memories table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_memories (
                    id VARCHAR(255) PRIMARY KEY,
                    source_agent VARCHAR(100) NOT NULL,
                    target_agent VARCHAR(100) NOT NULL,
                    content TEXT NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert the memory
            cursor.execute(
                """
                INSERT INTO agent_memories (id, source_agent, target_agent, content, metadata)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (memory_id, source_agent, target_agent, content, json.dumps(memory_metadata))
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()
        
        # Generate embedding and store in Pinecone
        embedding = generate_embedding(content, config)
        pinecone_index = initialize_pinecone(config)
        
        pinecone_index.upsert(
            vectors=[{
                "id": memory_id,
                "values": embedding,
                "metadata": filtered_metadata
            }],
            namespace=target_agent
        )
        
        return {
            "success": True,
            "memory_id": memory_id,
            "source_agent": source_agent,
            "target_agent": target_agent,
            "stored_in": ["postgres", "pinecone"]
        }
        
    except Exception as e:
        logger.error(f"Failed to share memory: {e}")
        return {
            "success": False,
            "error": str(e)
        }
