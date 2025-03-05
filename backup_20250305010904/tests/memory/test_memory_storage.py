import pytest
import os
import json
import uuid
from datetime import datetime

# Import the memory system components - adjust imports as needed
from cherry.memory import MemoryStore
from cherry.retrieval import retrieve_memories

@pytest.fixture
def config():
    """Load benchmark configuration."""
    config_path = os.path.join(os.path.dirname(__file__), '../../benchmarks/benchmark_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

@pytest.fixture
def memory_store(config):
    """Initialize memory store with test configuration."""
    # Create memory store with configuration
    store = MemoryStore(
        postgres_config=config['postgres'],
        pinecone_config=config['pinecone']
    )
    
    # Setup for test
    store.connect()
    
    yield store
    
    # Cleanup test data after test
    store.cleanup_test_data()

def test_store_and_retrieve_memory(memory_store, config):
    """Test storing a memory and retrieving it."""
    # Create unique test data
    test_id = str(uuid.uuid4())
    test_content = f"Test memory content {test_id}"
    
    # Create an embedding vector (using a simplified test vector)
    test_embedding = [0.1] * 1536  # Assuming 1536-dimensional embeddings
    
    # Create metadata according to the search_agent namespace schema
    test_metadata = {
        "source_type": "unit_test",
        "timestamp": int(datetime.now().timestamp()),
        "relevance_score": 0.95,
        "category": "test_category"
    }
    
    # 1. Store the memory
    memory_id = memory_store.store(
        content=test_content,
        embedding=test_embedding,
        metadata=test_metadata,
        namespace="search_agent"
    )
    
    # Verify memory was stored
    assert memory_id is not None, "Memory should be stored with a valid ID"
    
    # 2. Retrieve the memory
    retrieved_memories = retrieve_memories(
        query_embedding=test_embedding,
        namespace="search_agent",
        top_k=config['pinecone']['namespaces']['search_agent']['default_top_k']
    )
    
    # Verify memory was retrieved
    assert len(retrieved_memories) > 0, "Should retrieve at least one memory"
    
    # Find our test memory in the results
    found = False
    for memory in retrieved_memories:
        if memory.get("content") == test_content:
            found = True
            # Verify metadata was preserved
            assert memory.get("metadata", {}).get("source_type") == "unit_test"
            assert memory.get("metadata", {}).get("category") == "test_category"
            assert abs(memory.get("metadata", {}).get("relevance_score", 0) - 0.95) < 0.001
            break
    
    assert found, "The stored test memory should be retrieved"
