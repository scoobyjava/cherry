# Copilot Instructions for Cherry AI

## **Project Overview**
Cherry AI is a **self-improving AI orchestrator** designed to autonomously manage workflows, develop AI agents, optimize system processes, and interact via **natural language and voice**.  
Cherry must:  
- Write and manage code autonomously.  
- Handle database structures and schemas dynamically.  
- Deploy and manage AI agents based on task scope.  
- Continuously learn from interactions and online research.  
- Ensure contextual memory retention across conversations and tasks.  

## **Core Modules and Responsibilities**
- `agent.py` → Manages autonomous and task-based AI agents.  
- `config.py` → Stores dynamic configurations, environment settings, and preferences.  
- `memory.py` → Handles persistent memory storage and retrieval (ChromaDB, Pinecone, Zilliz).  
- `task_manager.py` → Coordinates task execution, prioritization, and dependency management.  
- `api.py` → Interfaces with external APIs (LLMs, databases, smart home systems, finance tools).  

## **Architectural Guidelines**
- AI agents must be **modular and adaptive**, supporting task-based and long-term learning strategies.  
- Cherry should implement **guardrails** to prevent major changes without user approval.  
- Persistent memory storage should ensure **long-term context retention** without redundancy.  

## **Development and Coding Standards**
- Follow a **modular, scalable** approach to AI agent design.  
- Prioritize **API-driven interactions** for adaptability.  
- Maintain **high-efficiency database queries** to optimize performance.  

## **Expected Copilot Behavior**
- Provide **context-aware suggestions** based on Cherry’s modular AI architecture.  
- Help refactor and optimize **AI agent code, memory handling, and task execution**.  
- Assist in integrating **Copilot with long-term memory and knowledge retention systems**.  
- Generate **improvements for API integration, data pipelines, and automation workflows**.  

---

# filepath: /workspaces/cherry/cherry/memory/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class MemoryInterface(ABC):
    @abstractmethod
    def store(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> str:
        """Store data in memory with optional namespace"""
        pass
        
    @abstractmethod
    def retrieve(self, query: str, namespace: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant memory entries based on semantic search"""
        pass
        
    @abstractmethod
    def update(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> bool:
        """Update existing memory entry"""
        pass
        
    @abstractmethod
    def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        """Remove a memory entry"""
        pass

# filepath: /workspaces/cherry/cherry/memory/providers/pinecone_memory.py
import pinecone
import os
from typing import Dict, List, Any, Optional
from ..base import MemoryInterface
from ...utils.embeddings import get_embedding

class PineconeMemory(MemoryInterface):
    def __init__(self, index_name: str):
        api_key = os.getenv("PINECONE_API_KEY")
        environment = os.getenv("PINECONE_ENVIRONMENT")
        
        pinecone.init(api_key=api_key, environment=environment)
        self.index = pinecone.Index(index_name)
        
    def store(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> str:
        # Generate embedding for the content
        content = data.get("content", "")
        vector = get_embedding(content)
        
        # Store in Pinecone
        self.index.upsert(
            vectors=[(key, vector, data)],
            namespace=namespace
        )
        return key
        
    # Implement other required methods (retrieve, update, delete)

# filepath: /workspaces/cherry/cherry/memory/factory.py
from typing import Optional
from .base import MemoryInterface
from .providers.pinecone_memory import PineconeMemory
# Import other providers as implemented

def get_memory_provider(provider_type: str, **kwargs) -> MemoryInterface:
    """Factory function to create appropriate memory provider"""
    if provider_type.lower() == "pinecone":
        return PineconeMemory(**kwargs)
    # Add other providers as implemented
    else:
        raise ValueError(f"Unsupported memory provider: {provider_type}")

# filepath: /workspaces/cherry/tests/memory/test_memory.py
import unittest
from cherry.memory.factory import get_memory_provider

class TestMemory(unittest.TestCase):
    def setUp(self):
        # Use a test namespace to avoid affecting production data
        self.memory = get_memory_provider("pinecone", index_name="cherry-test")
        
    def test_store_and_retrieve(self):
        # Test basic memory operations
        key = "test-memory-1"
        data = {
            "content": "This is a test memory about artificial intelligence",
            "metadata": {"source": "unit-test", "importance": "low"}
        }
        
        # Store data
        stored_key = self.memory.store(key, data)
        self.assertEqual(stored_key, key)
        
        # Retrieve data
        results = self.memory.retrieve("artificial intelligence")
        self.assertGreaterEqual(len(results), 1)
        # More assertions...
