import sys
import os
import time

# Add parent directory to path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.batch_embeddings import batch_generate_embeddings

# Mock embedding function for demonstration
def mock_generate_embedding(text):
    """Simulate embedding generation with occasional rate limits"""
    # Simulate rate limit errors occasionally
    if len(text) % 19 == 0:
        time.sleep(0.1)
        raise Exception("Rate limit exceeded, please try again later.")
    
    # Simulate processing time
    time.sleep(0.05)
    
    # Return a simple mock embedding (in real use, this would be a vector)
    return [float(ord(c)) / 1000 for c in text[:10]] + [0.0] * 1536

def main():
    # Example texts to embed
    texts = [
        f"This is a sample text document number {i} for embedding generation." 
        for i in range(100)
    ]
    
    print(f"Generating embeddings for {len(texts)} texts...")
    
    # Use our batch processing with the mock function
    start_time = time.time()
    embeddings = batch_generate_embeddings(
        texts=texts,
        generate_embedding_fn=mock_generate_embedding,
        batch_size=10,
        max_retries=3,
        show_progress=True
    )
    end_time = time.time()
    
    print(f"Generated {len(embeddings)} embeddings in {end_time - start_time:.2f} seconds")
    print(f"First embedding sample: {embeddings[0][:5]}...")

if __name__ == "__main__":
    main()
