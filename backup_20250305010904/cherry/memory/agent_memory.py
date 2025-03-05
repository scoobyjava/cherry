import os
import uuid
import logging
from datetime import datetime
import pinecone
import psycopg2
from psycopg2.extras import Json

logger = logging.getLogger(__name__)

# PostgreSQL connection management
def get_postgres_connection():
    """Establish and return a connection to PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            port=os.environ.get('POSTGRES_PORT', '5432'),
            database=os.environ.get('POSTGRES_DB', 'cherry_memory'),
            user=os.environ.get('POSTGRES_USER', 'postgres'),
            password=os.environ.get('POSTGRES_PASSWORD', 'postgres')
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
        raise

# Pinecone connection management
def init_pinecone():
    """Initialize and return Pinecone client."""
    try:
        pinecone.init(
            api_key=os.environ.get('PINECONE_API_KEY'),
            environment=os.environ.get('PINECONE_ENVIRONMENT', 'us-west1-gcp')
        )
        return pinecone
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone: {str(e)}")
        raise

def share_memory_between_agents(source_agent, target_agent, content):
    """
    Share memory from source agent to target agent, storing in PostgreSQL and Pinecone.
    
    Args:
        source_agent (str): ID or name of the agent sharing the memory
        target_agent (str): ID or name of the agent who will receive the memory
        content (str): The memory content to be shared
    
    Returns:
        str: The ID of the shared memory
    """
    memory_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    # Store in PostgreSQL
    try:
        conn = get_postgres_connection()
        cur = conn.cursor()
        
        # Create table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agent_shared_memories (
                id VARCHAR(36) PRIMARY KEY,
                source_agent VARCHAR(100) NOT NULL,
                target_agent VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                metadata JSONB
            )
        """)
        
        # Insert the shared memory
        cur.execute("""
            INSERT INTO agent_shared_memories (id, source_agent, target_agent, content, timestamp, metadata)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            memory_id, 
            source_agent, 
            target_agent, 
            content, 
            timestamp,
            Json({
                'source': source_agent,
                'target': target_agent,
                'shared': True,
                'timestamp': timestamp
            })
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"Memory shared in PostgreSQL: {memory_id} from {source_agent} to {target_agent}")
    except Exception as e:
        logger.error(f"Failed to store memory in PostgreSQL: {str(e)}")
        raise
    
    # Store in Pinecone
    try:
        pc = init_pinecone()
        
        # Check if the index exists, otherwise create it
        index_name = "cherry-memory"
        if index_name not in pc.list_indexes():
            pc.create_index(name=index_name, dimension=384)  # adjust dimension based on your embedding size
        
        # Get the index
        index = pc.Index(index_name)
        
        # Create vector embedding (assuming you have a function for this)
        # For this example, we'll use a placeholder
        vector_embedding = [0.0] * 384  # Replace with actual embedding generation
        
        # Upsert the vector with metadata
        index.upsert(
            vectors=[
                {
                    "id": memory_id,
                    "values": vector_embedding,
                    "metadata": {
                        "source_agent": source_agent,
                        "target_agent": target_agent, 
                        "content": content,
                        "timestamp": timestamp,
                        "namespace": target_agent  # Use target agent as namespace
                    }
                }
            ],
            namespace=target_agent  # Store in target agent's namespace
        )
        
        logger.info(f"Memory shared in Pinecone: {memory_id} from {source_agent} to {target_agent}")
    except Exception as e:
        logger.error(f"Failed to store memory in Pinecone: {str(e)}")
        raise
    
    return memory_id

def retrieve_shared_memories(agent_id, query=None, limit=10):
    """
    Retrieve memories shared with a specific agent.
    
    Args:
        agent_id (str): ID or name of the agent to retrieve memories for
        query (str, optional): Query string to search for specific memories
        limit (int, optional): Maximum number of memories to retrieve
    
    Returns:
        list: List of memory entries
    """
    try:
        conn = get_postgres_connection()
        cur = conn.cursor()
        
        if query:
            # Full-text search if query is provided
            cur.execute("""
                SELECT id, source_agent, content, timestamp 
                FROM agent_shared_memories 
                WHERE target_agent = %s AND content ILIKE %s
                ORDER BY timestamp DESC
                LIMIT %s
            """, (agent_id, f'%{query}%', limit))
        else:
            # Get all memories for this agent
            cur.execute("""
                SELECT id, source_agent, content, timestamp 
                FROM agent_shared_memories 
                WHERE target_agent = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """, (agent_id, limit))
        
        results = cur.fetchall()
        
        memories = [
            {
                "id": row[0],
                "source_agent": row[1],
                "content": row[2],
                "timestamp": row[3].isoformat() if hasattr(row[3], 'isoformat') else row[3]
            }
            for row in results
        ]
        
        cur.close()
        conn.close()
        return memories
        
    except Exception as e:
        logger.error(f"Failed to retrieve memories from PostgreSQL: {str(e)}")
        raise
