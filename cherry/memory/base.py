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
