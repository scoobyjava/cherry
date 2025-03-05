import json
import logging
import os
import psycopg2
import numpy as np
from psycopg2.extras import RealDictCursor
import openai
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from benchmark_config.json"""
    config_path = os.path.join(os.environ.get('WORKSPACE_ROOT', '/workspaces/cherry'), 
                              'benchmarks/benchmark_config.json')
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
            return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

def get_connection_params():
    """Extract PostgreSQL connection parameters from config with secret resolution"""
    config = load_config()
    postgres_config = config.get('postgres', {})
    
    # Resolve environment variables or secrets
    def resolve_param(param):
        if isinstance(param, str) and param.startswith("${SECRET:"):
            # Extract the variable name between ${SECRET: and }
            var_name = param[9:].split(":")[0].rstrip("}")
            return os.environ.get(var_name)
        return param
    
    return {
        'host': resolve_param(postgres_config.get('host')),
        'port': postgres_config.get('port', 5432),
        'database': resolve_param(postgres_config.get('database')),
        'user': resolve_param(postgres_config.get('user')),
        'password': resolve_param(postgres_config.get('password'))
    }

def get_embedding(text: str) -> List[float]:
    """Generate an embedding vector for the input text using OpenAI"""
    try:
        config = load_config()
        openai_config = config.get('openai', {})
        api_key = os.environ.get(openai_config.get('api_key')[9:-1])
        
        # Initialize OpenAI client
        openai.api_key = api_key
        
        # Get embedding
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"  # Default embedding model
        )
        embedding = response['data'][0]['embedding']
        return embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        raise

def fallback_retrieve_from_postgres(query_text: str, top_n: int, agent_id: str) -> List[Dict[Any, Any]]:
    """
    Perform semantic similarity search using pgvector in PostgreSQL as a fallback
    when Pinecone is unavailable.
    
    Args:
        query_text: The text query to search for
        top_n: Number of results to return
        agent_id: ID of the agent (corresponds to namespace in Pinecone)
    
    Returns:
        List of dictionary results with content and metadata
    """
    try:
        # Get query embedding
        query_embedding = get_embedding(query_text)
        
        # Connect to PostgreSQL
        conn_params = get_connection_params()
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Map agent_id to appropriate table
        table_mapping = {
            'search_agent': 'search_vectors',
            'recommendation_agent': 'recommendation_vectors',
            'qa_agent': 'qa_vectors'
        }
        
        table_name = table_mapping.get(agent_id)
        if not table_name:
            raise ValueError(f"Unknown agent_id: {agent_id}")
        
        # Prepare the query - assumes the table has embedding, content, and metadata columns
        query = f"""
        SELECT 
            content, 
            metadata,
            1 - (embedding <=> %s) as similarity_score
        FROM {table_name}
        ORDER BY embedding <=> %s
        LIMIT %s
        """
        
        # Execute query with vector comparison
        cursor.execute(query, (np.array(query_embedding).tolist(), np.array(query_embedding).tolist(), top_n))
        
        # Fetch results
        results = cursor.fetchall()
        
        # Close connection
        cursor.close()
        conn.close()
        
        # Process results to match expected format
        processed_results = []
        for row in results:
            processed_results.append({
                'content': row['content'],
                'metadata': row['metadata'],
                'similarity': row['similarity_score']
            })
        
        return processed_results
        
    except Exception as e:
        logger.error(f"Fallback PostgreSQL vector search failed: {e}")
        # Return an empty list if the fallback fails
        return []
