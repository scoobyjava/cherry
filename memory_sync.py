import os
import time
import logging
import schedule
import psycopg2
import pinecone
import numpy as np
from dotenv import load_dotenv
from datetime import datetime, timedelta

# For embedding generation (using OpenAI as an example)
import openai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memory_sync.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("memory_sync")

# Configuration from environment variables
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "cherry")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "cherry-memories")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "15"))

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

class MemorySynchronizer:
    def __init__(self):
        self.pg_conn = None
        self.pinecone_index = None
        self.last_check_time = datetime.now() - timedelta(days=1)  # Start by checking the last day

    def connect_to_postgres(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.pg_conn = psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD
            )
            logger.info("Successfully connected to PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False

    def connect_to_pinecone(self):
        """Establish connection to Pinecone"""
        try:
            pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
            self.pinecone_index = pinecone.Index(PINECONE_INDEX)
            logger.info("Successfully connected to Pinecone")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Pinecone: {e}")
            return False

    def get_new_memories(self):
        """Fetch new or updated memories from PostgreSQL"""
        if not self.pg_conn:
            logger.error("No PostgreSQL connection available")
            return []

        try:
            with self.pg_conn.cursor() as cursor:
                # Adjust this query based on your actual database schema
                query = """
                    SELECT id, content, metadata 
                    FROM memories 
                    WHERE created_at > %s OR updated_at > %s
                    ORDER BY created_at DESC
                """
                cursor.execute(query, (self.last_check_time, self.last_check_time))
                memories = cursor.fetchall()
                
                if memories:
                    logger.info(f"Found {len(memories)} new or updated memories")
                
                # Update the last check time
                self.last_check_time = datetime.now()
                
                return memories
        except Exception as e:
            logger.error(f"Error fetching memories from PostgreSQL: {e}")
            return []

    def check_missing_embeddings(self, memories):
        """Check which memories are missing embeddings in Pinecone"""
        if not self.pinecone_index:
            logger.error("No Pinecone connection available")
            return memories

        try:
            memory_ids = [mem[0] for mem in memories]
            
            # Check which IDs exist in Pinecone
            if memory_ids:
                fetch_response = self.pinecone_index.fetch(ids=memory_ids)
                existing_ids = set(fetch_response.get('vectors', {}).keys())
                missing_memories = [mem for mem in memories if mem[0] not in existing_ids]
                
                if missing_memories:
                    logger.info(f"Found {len(missing_memories)} memories missing embeddings")
                
                return missing_memories
            return []
        except Exception as e:
            logger.error(f"Error checking embeddings in Pinecone: {e}")
            return memories

    def generate_embedding(self, text):
        """Generate an embedding vector for the given text"""
        try:
            # Using OpenAI's embedding model
            response = openai.Embedding.create(
                input=text,
                model=EMBEDDING_MODEL
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def upsert_embeddings(self, memories_to_embed):
        """Generate and upsert embeddings for memories"""
        if not memories_to_embed:
            return
        
        if not self.pinecone_index:
            logger.error("No Pinecone connection available")
            return

        vectors_to_upsert = []
        
        for memory_id, content, metadata in memories_to_embed:
            try:
                # Generate embedding for the memory content
                embedding = self.generate_embedding(content)
                
                if embedding:
                    # Prepare vector for upserting
                    vector = {
                        "id": memory_id,
                        "values": embedding,
                        "metadata": metadata or {}
                    }
                    vectors_to_upsert.append(vector)
            except Exception as e:
                logger.error(f"Error processing memory {memory_id}: {e}")
        
        if vectors_to_upsert:
            try:
                # Upsert vectors in batches if necessary
                batch_size = 100
                for i in range(0, len(vectors_to_upsert), batch_size):
                    batch = vectors_to_upsert[i:i+batch_size]
                    self.pinecone_index.upsert(vectors=batch)
                
                logger.info(f"Successfully upserted {len(vectors_to_upsert)} embeddings to Pinecone")
            except Exception as e:
                logger.error(f"Error upserting embeddings to Pinecone: {e}")

    def sync_memories(self):
        """Main synchronization function"""
        logger.info("Starting memory synchronization...")
        
        # Ensure connections
        if not self.pg_conn and not self.connect_to_postgres():
            return
        
        if not self.pinecone_index and not self.connect_to_pinecone():
            return
        
        # Get new memories
        memories = self.get_new_memories()
        
        if memories:
            # Check which ones are missing embeddings
            missing_embeddings = self.check_missing_embeddings(memories)
            
            # Generate and upsert missing embeddings
            self.upsert_embeddings(missing_embeddings)
        
        logger.info("Memory synchronization completed")

    def start_periodic_sync(self):
        """Start periodic synchronization"""
        logger.info(f"Starting periodic sync every {CHECK_INTERVAL_MINUTES} minutes")
        
        # Run once immediately at startup
        self.sync_memories()
        
        # Schedule periodic runs
        schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(self.sync_memories)
        
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    synchronizer = MemorySynchronizer()
    try:
        synchronizer.start_periodic_sync()
    except KeyboardInterrupt:
        logger.info("Memory synchronization stopped by user")
    except Exception as e:
        logger.error(f"Memory synchronization failed: {e}")
        raise
