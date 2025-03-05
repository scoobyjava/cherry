import json
import os
import pinecone

def load_config():
    """Load configuration from the benchmark config file."""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "benchmarks", 
        "benchmark_config.json"
    )
    
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

def init_pinecone():
    """Initialize Pinecone client and create index."""
    config = load_config()
    pinecone_config = config.get("pinecone", {})
    
    # Initialize Pinecone client
    api_key = pinecone_config.get("api_key")
    environment = pinecone_config.get("environment")
    
    if not api_key or api_key == "your-pinecone-api-key":
        raise ValueError("Please set a valid Pinecone API key in the config file")
    
    pinecone.init(api_key=api_key, environment=environment)
    print(f"Initialized Pinecone client in environment: {environment}")
    
    # Check if index exists
    index_name = "cherry-memory-index"
    if index_name in pinecone.list_indexes():
        print(f"Index '{index_name}' already exists")
        return
    
    # Create the index
    pinecone.create_index(
        name=index_name,
        dimension=1536,  # OpenAI embeddings dimension
        metric="cosine",
        pod_type="p1"  # Adjust based on your needs
    )
    print(f"Created Pinecone index '{index_name}' with dimension=1536 and cosine similarity metric")

if __name__ == "__main__":
    init_pinecone()
