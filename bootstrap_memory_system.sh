#!/bin/bash

# Set exit on error
set -e

mkdir -p /workspaces/cherry/cherry/memory/providers \
         /workspaces/cherry/cherry/utils \
         /workspaces/cherry/cherry/agents \
         /workspaces/cherry/cherry/core \
         /workspaces/cherry/tests/memory

touch /workspaces/cherry/cherry/__init__.py
touch /workspaces/cherry/cherry/memory/__init__.py
touch /workspaces/cherry/cherry/memory/providers/__init__.py
touch /workspaces/cherry/cherry/utils/__init__.py
touch /workspaces/cherry/cherry/agents/__init__.py
touch /workspaces/cherry/cherry/core/__init__.py
touch /workspaces/cherry/tests/__init__.py
touch /workspaces/cherry/tests/memory/__init__.py

# 1. base.py
cat << 'EOF' > /workspaces/cherry/cherry/memory/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class MemoryInterface(ABC):
    @abstractmethod
    def store(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> str:
        pass
    @abstractmethod
    def retrieve(self, query: str, namespace: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        pass
    @abstractmethod
    def update(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> bool:
        pass
    @abstractmethod
    def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        pass
EOF

# 2. embeddings.py
cat << 'EOF' > /workspaces/cherry/cherry/utils/embeddings.py
import numpy as np
from typing import List

def get_embedding(text: str, model: str = "text-embedding-ada-002") -> List[float]:
    dimension = get_embedding_dimension(model)
    return list(np.random.normal(0, 1, dimension).astype(float))

def get_embedding_dimension(model: str = "text-embedding-ada-002") -> int:
    dimensions = {
        "text-embedding-ada-002": 1536,
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072
    }
    return dimensions.get(model, 1536)
EOF

# 3. pinecone_memory.py
cat << 'EOF' > /workspaces/cherry/cherry/memory/providers/pinecone_memory.py
import pinecone
import os
from typing import Dict, List, Any, Optional
from ..base import MemoryInterface
from ...utils.embeddings import get_embedding

class PineconeMemory(MemoryInterface):
    def __init__(self, index_name: str):
        api_key = os.getenv("PINECONE_API_KEY")
        env = os.getenv("PINECONE_ENVIRONMENT")
        pinecone.init(api_key=api_key, environment=env)
        self.index = pinecone.Index(index_name)
    def store(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> str:
        vector = get_embedding(data.get("content", ""))
        self.index.upsert([(key, vector, data)], namespace=namespace)
        return key
    def retrieve(self, query: str, namespace: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        results = self.index.query(get_embedding(query), top_k=limit, namespace=namespace, include_metadata=True)
        return [m["metadata"] for m in results.matches]
    def update(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> bool:
        try:
            vector = get_embedding(data.get("content", ""))
            self.index.upsert([(key, vector, data)], namespace=namespace)
            return True
        except:
            return False
    def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        try:
            self.index.delete(ids=[key], namespace=namespace)
            return True
        except:
            return False
EOF

# 4. chroma_memory.py
cat << 'EOF' > /workspaces/cherry/cherry/memory/providers/chroma_memory.py
import chromadb
import os
from typing import Dict, List, Any, Optional
from ..base import MemoryInterface
from ...utils.embeddings import get_embedding

class ChromaMemory(MemoryInterface):
    def __init__(self, collection_name: str, persist_directory: Optional[str] = None):
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name=collection_name)
    def store(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> str:
        vector = get_embedding(data.get("content", ""))
        meta = {k: v for k, v in data.items() if k != "content"}
        if namespace:
            meta["namespace"] = namespace
        self.collection.add(ids=[key], embeddings=[vector], metadatas=[meta], documents=[data.get("content","")])
        return key
    def retrieve(self, query: str, namespace: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        where = {"namespace": namespace} if namespace else None
        qvec = get_embedding(query)
        results = self.collection.query(query_embeddings=[qvec], n_results=limit, where=where)
        entries = []
        for i in range(len(results["ids"][0])):
            entries.append({"content": results["documents"][0][i], **results["metadatas"][0][i]})
        return entries
    def update(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> bool:
        try:
            vector = get_embedding(data.get("content", ""))
            meta = {k: v for k, v in data.items() if k != "content"}
            if namespace: meta["namespace"] = namespace
            self.collection.update(ids=[key], embeddings=[vector], metadatas=[meta], documents=[data.get("content","")])
            return True
        except:
            return False
    def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        try:
            self.collection.delete(ids=[key])
            return True
        except:
            return False
EOF

# 5. factory.py
cat << 'EOF' > /workspaces/cherry/cherry/memory/factory.py
from typing import Any
from .base import MemoryInterface
from .providers.pinecone_memory import PineconeMemory
from .providers.chroma_memory import ChromaMemory

def get_memory_provider(provider_type: str, **kwargs: Any) -> MemoryInterface:
    if not provider_type:
        raise ValueError("No provider specified.")
    if provider_type.lower() == "pinecone": return PineconeMemory(**kwargs)
    if provider_type.lower() == "chroma": return ChromaMemory(**kwargs)
    raise ValueError(f"Unsupported memory provider: {provider_type}")
EOF

# 6. manager.py
cat << 'EOF' > /workspaces/cherry/cherry/memory/manager.py
import time
import uuid
from typing import Dict, List, Any, Optional
from .factory import get_memory_provider

class MemoryManager:
    def __init__(self, primary_provider: str, primary_config: Dict[str, Any],
                 cache_provider: Optional[str] = None, cache_config: Optional[Dict[str, Any]] = None, cache_ttl: int = 3600):
        self.primary = get_memory_provider(primary_provider, **primary_config)
        self.cache = get_memory_provider(cache_provider, **cache_config) if cache_provider else None
        self.cache_ttl = cache_ttl
        self.cache_index = {}
    def generate_key(self) -> str:
        return str(uuid.uuid4())
    def store(self, data: Dict[str, Any], namespace: Optional[str] = None, key: Optional[str] = None) -> str:
        memory_key = key if key else self.generate_key()
        data["timestamp"] = int(time.time())
        self.primary.store(memory_key, data, namespace)
        if self.cache:
            self.cache.store(memory_key, data, namespace)
            self.cache_index[memory_key] = time.time() + self.cache_ttl
        return memory_key
    def retrieve(self, query: str, namespace: Optional[str] = None, limit: int = 5, recency_bias: float = 0.3) -> List[Dict[str, Any]]:
        results = self.primary.retrieve(query, namespace, limit=limit*2)
        if not results:
            return []
        now = time.time()
        for r in results:
            ts = r.get("timestamp", now)
            age = now - ts
            recency_factor = 1.0 / (1.0 + (age / 86400) * recency_bias)
            imp = r.get("metadata", {}).get("importance", 0.5)
            if isinstance(imp, str):
                imp_map = {"low":0.3, "medium":0.5, "high":0.8, "critical":1.0}
                imp = imp_map.get(imp.lower(), 0.5)
            base_score = r.get("_score", 0.8)
            r["_score"] = base_score * recency_factor * (1 + imp)
        results.sort(key=lambda x: x["_score"], reverse=True)
        return results[:limit]
    def update(self, key: str, data: Dict[str, Any], namespace: Optional[str] = None) -> bool:
        data["last_updated"] = int(time.time())
        ok = self.primary.update(key, data, namespace)
        if ok and self.cache:
            self.cache.update(key, data, namespace)
            self.cache_index[key] = time.time() + self.cache_ttl
        return ok
    def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        ok = self.primary.delete(key, namespace)
        if ok and self.cache:
            self.cache.delete(key, namespace)
            self.cache_index.pop(key, None)
        return ok
    def maintain_cache(self):
        if not self.cache:
            return
        now = time.time()
        expired = [k for k,v in self.cache_index.items() if v < now]
        for k in expired:
            self.cache.delete(k)
            self.cache_index.pop(k, None)
EOF

# 7. Tests

# test_memory.py
cat << 'EOF' > /workspaces/cherry/tests/memory/test_memory.py
import unittest
from cherry.memory.factory import get_memory_provider

class TestMemory(unittest.TestCase):
    def setUp(self):
        self.memory = get_memory_provider("pinecone", index_name="cherry-test")
    def test_store_and_retrieve(self):
        key = "test-memory-1"
        data = {"content":"A test memory about AI", "metadata":{"source":"unittest","importance":"low"}}
        stored_key = self.memory.store(key, data)
        self.assertEqual(stored_key, key)
        results = self.memory.retrieve("AI")
        self.assertTrue(len(results) >= 1)
    def test_update(self):
        key = "test-update-memory"
        data = {"content":"Original content","metadata":{"source":"unittest"}}
        self.memory.store(key, data)
        updated_data = {"content":"Updated content","metadata":{"updated":True}}
        self.assertTrue(self.memory.update(key, updated_data))
        results = self.memory.retrieve("Updated")
        self.assertTrue(len(results) >= 1)
    def test_delete(self):
        key = "test-delete-memory"
        data = {"content":"Deletable content","metadata":{}}
        self.memory.store(key, data)
        self.assertTrue(self.memory.delete(key))
        results = self.memory.retrieve("Deletable content")
        self.assertEqual(len(results), 0)
EOF

# test_memory_manager.py
cat << 'EOF' > /workspaces/cherry/tests/memory/test_memory_manager.py
import unittest
import time
from cherry.memory.manager import MemoryManager

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        self.manager = MemoryManager(
            primary_provider="pinecone",
            primary_config={"index_name":"cherry-test"},
            cache_provider="chroma",
            cache_config={"collection_name":"memory-cache"},
            cache_ttl=60
        )
    def test_store_and_retrieve(self):
        data = {"content":"Info about ML","metadata":{"importance":"high"}}
        key = self.manager.store(data)
        self.assertIsNotNone(key)
        results = self.manager.retrieve("ML")
        self.assertTrue(len(results)>=1)
    def test_smart_ranking(self):
        self.manager.store({"content":"Old low importance","metadata":{"importance":"low"},"timestamp":int(time.time())-86400*5})
        self.manager.store({"content":"New medium importance","metadata":{"importance":"medium"},"timestamp":int(time.time())-3600})
        self.manager.store({"content":"High importance older","metadata":{"importance":"high"},"timestamp":int(time.time())-43200})
        results = self.manager.retrieve("importance", recency_bias=0.3)
        self.assertIn("high", results[0].get("metadata",{}).get("importance",""))
EOF

# 8. Agents (Optional)
cat << 'EOF' > /workspaces/cherry/cherry/agents/base_agent.py
from abc import ABC, abstractmethod
from cherry.memory.manager import MemoryManager

class BaseAgent(ABC):
    def __init__(self, name: str, memory_manager: MemoryManager):
        self.name = name
        self.memory_manager = memory_manager
    
    @abstractmethod
    def handle_task(self, task: str) -> str:
        pass
EOF

cat << 'EOF' > /workspaces/cherry/cherry/agents/ai_agent.py
from typing import Any, Dict
from .base_agent import BaseAgent

class AIAgent(BaseAgent):
    def handle_task(self, task: str) -> str:
        context_results = self.memory_manager.retrieve(task, limit=3)
        context_text = "\n".join(x.get("content","") for x in context_results)
        self.memory_manager.store({"content":f"Agent response for '{task}'","metadata":{"importance":"medium"}})
        return f"Responding to '{task}'. Context:\n{context_text}"
EOF

# 9. Orchestrator (Optional)
cat << 'EOF' > /workspaces/cherry/cherry/core/orchestrator.py
from cherry.agents.ai_agent import AIAgent
from cherry.memory.manager import MemoryManager

class Orchestrator:
    def __init__(self):
        self.memory_manager = MemoryManager(
            primary_provider="pinecone",
            primary_config={"index_name":"cherry-production"},
            cache_provider="chroma",
            cache_config={"collection_name":"cherry-cache"},
            cache_ttl=600
        )
        self.agent = AIAgent("default-agent", self.memory_manager)
    def process_task(self, task: str) -> str:
        return self.agent.handle_task(task)
EOF

# 10. CLI (Optional)
cat << 'EOF' > /workspaces/cherry/cherry/cli.py
from cherry.core.orchestrator import Orchestrator

def main():
    orchestrator = Orchestrator()
    print("Cherry CLI - type 'exit' to quit.")
    while True:
        task = input("Enter task: ")
        if task.lower() == "exit":
            break
        print(orchestrator.process_task(task))

if __name__ == "__main__":
    main()
EOF

echo "Bootstrap complete. You can now run:"
echo "pip install pinecone-client chromadb numpy"
echo "python -m unittest discover /workspaces/cherry/tests"
echo "or python -m cherry.cli for the CLI (requires Pinecone API keys etc.)"
