import logging
from typing import List, Dict, Any, Optional

import pinecone
import psycopg2
from psycopg2.extras import RealDictCursor

from cherry.memory.embeddings import generate_embedding
from cherry.core.config import get_database_config

logger = logging.getLogger(__name__)

def retrieve_memories(query_text: str, top_n: int, agent_id=None) -> List[Dict[str, Any]]:
    """
    Retrieve memories based on semantic similarity to the query text.
    
    Args:
        query_text: The text to search for similar memories
        top_n: Number of top similar memories to retrieve
        agent_id: Optional agent ID to filter memories by namespace
    
    Returns:
        List of memory records with content and metadata
    """
    try:
        # Step 1: Generate embedding for the query text
        query_embedding = generate_embedding(query_text)
        
        # Step 2: Query Pinecone for similar embeddings
        pinecone_index = pinecone.Index("memories")  # Assuming "memories" is the index name
        
        # Prepare query parameters
        query_params = {
            "vector": query_embedding,
            "top_k": top_n,
            "include_metadata": True,
        }
        
        # Add namespace filter if agent_id is provided
        if agent_id:
            query_params["namespace"] = agent_id
            
        # Execute the query
        query_results = pinecone_index.query(**query_params)
        
        if not query_results.matches:
            logger.info(f"No memories found for query: {query_text}")
            return []
            
        # Extract IDs and similarity scores from Pinecone results
        memory_ids = [match.id for match in query_results.matches]
        similarities = {match.id: match.score for match in query_results.matches}
        
        # Step 3: Retrieve full memory records from PostgreSQL
        db_config = get_database_config()
        conn = psycopg2.connect(
            dbname=db_config["dbname"],
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=db_config["port"]
        )
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Create a parameterized query with the right number of placeholders
        placeholders = ','.join(['%s'] * len(memory_ids))
        query = f"""
            SELECT * FROM memories 
            WHERE id IN ({placeholders})
        """
        
        # Execute the query with memory_ids
        cursor.execute(query, memory_ids)
        
        # Fetch all results as dictionaries
        db_records = cursor.fetchall()
        
        # Close database connection
        cursor.close()
        conn.close()
        
        # Map records by ID for easy lookup
        record_map = {str(record["id"]): record for record in db_records}
        
        # Step 4: Structure the results with content and metadata
        memories = []
        for memory_id in memory_ids:
            if memory_id in record_map:
                record = record_map[memory_id]
                memory = {
                    "id": record["id"],
                    "content": record["content"],
                    "similarity": similarities[memory_id],
                    "metadata": {
                        "created_at": record["created_at"],
                        "agent_id": record["agent_id"],
                        "source": record.get("source"),
                        "importance": record.get("importance", 0),
                        # Include other available metadata
                        "tags": record.get("tags", []),
                        "context": record.get("context", {})
                    }
                }
                memories.append(memory)
            
        logger.info(f"Retrieved {len(memories)} memories for query: {query_text}")
        return memories
        
    except Exception as e:
        logger.error(f"Error retrieving memories: {str(e)}")
        raise
