import os
from dotenv import load_dotenv
import openai
from cherry.memory.pinecone_memory import PineconeMemory

# Load environment variables
load_dotenv()

# Initialize OpenAI client for embeddings
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_embedding(text):
    """Get embedding for a text using OpenAI API"""
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def main():
    # Initialize Pinecone memory
    memory = PineconeMemory(
        index_name="cherry-test",
        dimension=1536  # Dimension for Ada 002 embeddings
    )
    
    # Example data for different agents
    researcher_texts = [
        "Machine learning has revolutionized natural language processing",
        "Transformer models like GPT-4 use self-attention mechanisms",
        "Transfer learning allows models to apply knowledge to new tasks"
    ]
    
    assistant_texts = [
        "How can I help you with your project today?",
        "I'll search for some relevant resources for you",
        "Let me summarize this document for better understanding"
    ]
    
    # Create embeddings and upsert for researcher agent
    researcher_embeddings = [get_embedding(text) for text in researcher_texts]
    researcher_metadata = [{"source": "research", "category": "nlp"} for _ in researcher_texts]
    researcher_ids = memory.upsert(
        vectors=researcher_embeddings,
        texts=researcher_texts,
        metadata=researcher_metadata,
        agent_id="researcher"
    )
    print(f"Upserted {len(researcher_ids)} vectors for researcher agent")
    
    # Create embeddings and upsert for assistant agent
    assistant_embeddings = [get_embedding(text) for text in assistant_texts]
    assistant_metadata = [{"source": "assistant", "category": "support"} for _ in assistant_texts]
    assistant_ids = memory.upsert(
        vectors=assistant_embeddings,
        texts=assistant_texts,
        metadata=assistant_metadata,
        agent_id="assistant"
    )
    print(f"Upserted {len(assistant_ids)} vectors for assistant agent")
    
    # Query example - only searching within researcher namespace
    query = "How do transformer models work?"
    query_embedding = get_embedding(query)
    
    researcher_results = memory.query(
        query_vector=query_embedding,
        agent_id="researcher",
        top_k=2
    )
    
    print(f"\nQuery: {query}")
    print(f"Top researcher results:")
    for i, match in enumerate(researcher_results):
        print(f"{i+1}. {match['metadata']['text']} (Score: {match['score']})")
    
    # Show namespace stats
    print("\nNamespace statistics:")
    for namespace, stats in memory.get_namespace_stats().items():
        print(f"- {namespace}: {stats.get('vector_count', 0)} vectors")

if __name__ == "__main__":
    main()
