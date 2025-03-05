import logging
from typing import List, Dict, Any, Optional
import psycopg2
from pinecone import Pinecone

from config import PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME, DB_CONFIG
from utils.embedding import generate_embedding

logger = logging.getLogger(__name__)

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index(PINECONE_INDEX_NAME)

def get_db_connection():
    """Create and return a connection to the PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG)

def retrieve_memories(query_text: str, top_n: int, agent_id=None) -> List[Dict[str, Any]]:
    """
    Retrieve memories from Pinecone and PostgreSQL based on semantic similarity to query_text.
    
    Args:
        query_text (str): The text to query for similar memories.
        top_n (int): The number of top similar memories to retrieve.
        agent_id (str, optional): If provided, restrict search to memories from this agent.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing memory contents and metadata.
    """
    try:
        # 1. Generate embedding from query text
        query_embedding = generate_embedding(query_text)
        
        # 2. Query Pinecone for similar embeddings
        try:
            query_params = {
                "vector": query_embedding,
                "top_k": top_n,
                "include_metadata": True
            }
            
            # Add namespace filter if agent_id is provided
            if agent_id:
                query_params["namespace"] = agent_id
                
            pinecone_response = pinecone_index.query(**query_params)
        except Exception as e:
            logger.error(f"Error querying Pinecone: {e}")
            return []
        
        # Extract memory IDs from Pinecone results
        matches = pinecone_response.get("matches", [])
        memory_ids = [match.get("id") for match in matches]
        
        if not memory_ids:
            logger.info("No similar memories found in Pinecone")
            return []
        
        # Create a mapping of ID to similarity score and metadata
        similarity_map = {match.get("id"): match.get("score") for match in matches}
        pinecone_metadata = {match.get("id"): match.get("metadata", {}) for match in matches}
        
        # 3. Retrieve full memory records from PostgreSQL
        results = []
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    placeholders = ", ".join(["%s"] * len(memory_ids))
                    query = f"SELECT id, content, metadata, created_at, agent_id FROM memories WHERE id IN ({placeholders})"
                    cursor.execute(query, memory_ids)
                    memories = cursor.fetchall()
                    
                    # 4. Format and return the results
                    retrieved_ids = set()
                    for memory in memories:
                        memory_id = memory[0]
                        retrieved_ids.add(memory_id)
                        
                        results.append({
                            "id": memory_id,
                            "content": memory[1],
                            "metadata": memory[2],
                            "created_at": memory[3],
                            "agent_id": memory[4],
                            "similarity": similarity_map.get(memory_id, 0.0)
                        })
                    
                    # Log any IDs that were found in Pinecone but not in PostgreSQL
                    missing_ids = set(memory_ids) - retrieved_ids
                    if missing_ids:
                        logger.warning(f"Found {len(missing_ids)} IDs in Pinecone that were missing from PostgreSQL: {missing_ids}")
        except Exception as e:
            logger.error(f"Error retrieving memories from PostgreSQL: {e}")
            return []
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        logger.info(f"Retrieved {len(results)} memories based on query: {query_text[:50]}...")
        return results
    except Exception as e:
        logger.error(f"Unexpected error in retrieve_memories: {e}")
        return []
