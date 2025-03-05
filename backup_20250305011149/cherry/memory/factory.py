from typing import Optional
from .base import MemoryInterface
from .providers.pinecone_memory import PineconeMemory
from .providers.chroma_memory import ChromaMemory

def get_memory_provider(provider_type: str, **kwargs) -> MemoryInterface:
    """Factory function to create appropriate memory provider"""
    if provider_type.lower() == "pinecone":
        return PineconeMemory(**kwargs)
    elif provider_type.lower() == "chroma":
        return ChromaMemory(**kwargs)
    else:
        raise ValueError(f"Unsupported memory provider: {provider_type}")