import os
import json
import pinecone
import psycopg2
from psycopg2.extras import RealDictCursor
import openai
from typing import List, Dict, Any, Optional

def load_config():
    """Load configuration from benchmark_config.json"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              'benchmarks', 'benchmark_config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    return process_config_secrets(config)

def process_config_secrets(config):
    """Process secrets and environment variables in config"""
    if isinstance(config, dict):
        return {k: process_config_secrets(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [process_config_secrets(item) for item in config]
    elif isinstance(config, str) and config.startswith("${SECRET:"):
        parts = config[9:-1].split(":", 1)
        secret_name = parts[0]
        return os.environ.get(secret_name, "")
    else:
        return config

def get_pinecone_connection():
    """Get connection to Pinecone"""
    config = load_config()
    pinecone_config = config['pinecone']
    
    pinecone.init(
        api_key=pinecone_config['api_key'],
        environment=pinecone_config['environment']
    )
    return pinecone.Index(pinecone_config['index_name'])

def get_postgres_connection():
    """Get connection to PostgreSQL"""
    config = load_config()
    pg_config = config['postgres']
    
    conn = psycopg2.connect(
        host=pg_config['host'],
        port=pg_config['port'],
        database=pg_config['database'],
        user=pg_config['user'],
        password=pg_config['password']
    )
    return conn

def generate_embedding(text: str) -> List[float]:
    """Generate embedding for the given text using OpenAI"""
    config = load_config()
    openai_config = config['openai']
    
    openai.api_key = openai_config['api_key']
    if 'organization_id' in openai_config and openai_config['organization_id']:
        openai.organization = openai_config['organization_id']
    
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    
    return response['data'][0]['embedding']

def retrieve_memories(query_text: str, top_n: int, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve memories based on semantic similarity to query_text.
    
    Args:
        query_text (str): The query text to search for similar memories
        top_n (int): Number of memories to retrieve
        agent_id (str, optional): Filter by specific agent namespace
    
    Returns:
        list: List of dictionaries containing memory contents and metadata
    """
    # Generate embedding for the query text
    query_embedding = generate_embedding(query_text)
    
    # Get Pinecone connection and query for similar embeddings
    pinecone_index = get_pinecone_connection()
    query_results = pinecone_index.query(
        vector=query_embedding,
        top_k=top_n,
        namespace=agent_id,
        include_metadata=True
    )
    
    # Extract IDs and scores from Pinecone results
    memory_matches = [(match['id'], match['score'], match.get('metadata', {})) 
                      for match in query_results['matches']]
    
    if not memory_matches:
        return []
    
    # Get PostgreSQL connection
    pg_conn = get_postgres_connection()
    
    try:
        # Query PostgreSQL to get full memory records
        memory_ids = [match[0] for match in memory_matches]
        id_to_score = {match[0]: match[1] for match in memory_matches}
        id_to_metadata = {match[0]: match[2] for match in memory_matches}
        
        with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            placeholders = ', '.join(['%s'] * len(memory_ids))
            query = f"""
            SELECT * FROM memories 
            WHERE memory_id IN ({placeholders})
            """
            cursor.execute(query, memory_ids)
            memories = cursor.fetchall()
        
        # Format results and add similarity scores
        results = []
        for memory in memories:
            memory_dict = dict(memory)
            memory_id = memory_dict['memory_id']
            
            # Add similarity score and Pinecone metadata
            if memory_id in id_to_score:
                memory_dict['similarity_score'] = id_to_score[memory_id]
                memory_dict['vector_metadata'] = id_to_metadata[memory_id]
            
            results.append(memory_dict)
        
        # Sort results by similarity score (highest first)
        results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        # Add rank
        for i, result in enumerate(results):
            result['rank'] = i + 1
        
        return results
        
    finally:
        pg_conn.close()
