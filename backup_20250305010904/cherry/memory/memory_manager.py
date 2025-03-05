import chromadb
from typing import List, Dict, Any, Optional
import numpy as np

class MemoryManager:
    def __init__(self, collection_name: str = "cherry_memories"):
        """Initialize the memory manager with ChromaDB backend."""
        self.client = chromadb.Client()
        # Create or get existing collection
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
    def store_memory(self, memory: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store a memory with optional metadata."""
        memory_id = memory.get("id", str(hash(str(memory))))
        self.collection.add(
            documents=[str(memory["content"])],
            metadatas=[metadata or {}],
            ids=[memory_id]
        )
        return memory_id
        
    def retrieve_memories(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant memories based on a query string."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        memories = []
        for i, doc in enumerate(results["documents"][0]):
            memory = {
                "content": doc,
                "id": results["ids"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "relevance_score": results.get("distances", [[0] * len(results["ids"][0])])[0][i]
            }
            memories.append(memory)
            
        return memories
    
    def filter_memories_for_agent(self, memories: List[Dict[str, Any]], agent_type: str) -> List[Dict[str, Any]]:
        """Filter memories based on relevance to a specific agent type."""
        # Basic filtering logic - could be enhanced with more sophisticated rules
        agent_relevance = {
            "researcher": lambda mem: "research" in mem["content"].lower() or "data" in mem["content"].lower(),
            "planner": lambda mem: "plan" in mem["content"].lower() or "strategy" in mem["content"].lower(),
            # Add more agent types and filtering rules as needed
        }
        
        # Default filter passes everything if agent type not recognized
        filter_func = agent_relevance.get(agent_type.lower(), lambda _: True)
        return [mem for mem in memories if filter_func(mem)]
        
    def calculate_memory_relevance(self, memory: Dict[str, Any], query: str) -> float:
        """Calculate how relevant a memory is to the current query."""
        # Simple relevance calculation using term overlap
        # In a real implementation, consider using embedding similarity
        memory_terms = set(memory["content"].lower().split())
        query_terms = set(query.lower().split())
        overlap = len(memory_terms.intersection(query_terms))
        return overlap / max(1, len(query_terms))
