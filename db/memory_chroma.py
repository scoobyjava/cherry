# memory_chroma.py
import chromadb
import time
import os
from typing import List, Dict, Any, Optional
from logger import logger
from config import Config
import numpy as np

class ChromaMemory:
    """Persistent memory module using ChromaDB vector storage."""

    def __init__(self,
                 collection_name: str = "cherry_memory",
                 persist_directory: Optional[str] = None):
        self.persist_directory = persist_directory or Config.CHROMADB_PERSIST_DIRECTORY
        self.collection_name = collection_name
        os.makedirs(self.persist_directory, exist_ok=True)

        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            logger.info(f"🍒 ChromaMemory initialized with collection '{self.collection_name}' at '{self.persist_directory}'")
        except Exception as e:
            logger.error(f"🚨 Failed initializing ChromaMemory: {e}")
            raise

    def insert_text(self,
                    text: str,
                    embedding: List[float],
                    metadata: Optional[Dict[str, Any]] = None,
                    doc_id: Optional[str] = None) -> str:
        metadata = metadata or {}
        metadata["timestamp"] = time.time()
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        doc_id = doc_id or f"doc_{int(time.time() * 1000)}"

        try:
            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logger.debug(f"✅ Inserted document '{doc_id}' successfully.")
            return doc_id
        except Exception as e:
            logger.error(f"🚨 Error inserting document '{doc_id}': {e}")
            raise

    def search_similar(self,
                       query_embedding: List[float],
                       limit: int = 5,
                       filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if isinstance(query_embedding, np.ndarray):
            query_embedding = query_embedding.tolist()

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=filter_criteria
            )
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            ids = results.get("ids", [[]])[0]
            distances = results.get("distances", [[]])[0]

            formatted_results = [
                {
                    "id": doc_id,
                    "document": doc,
                    "metadata": meta,
                    "distance": dist
                }
                for doc_id, doc, meta, dist in zip(ids, documents, metadatas, distances)
            ]

            logger.debug(f"🔍 Found {len(formatted_results)} similar documents.")
            return formatted_results
        except Exception as e:
            logger.error(f"🚨 Error during similarity search: {e}")
            raise

    def delete_document(self, doc_id: str) -> bool:
        try:
            self.collection.delete(ids=[doc_id])
            logger.debug(f"🗑️ Deleted document '{doc_id}' successfully.")
            return True
        except Exception as e:
            logger.error(f"🚨 Error deleting document '{doc_id}': {e}")
            return False

    def collection_stats(self) -> Dict[str, Any]:
        try:
            total_docs = len(self.collection.get().get("ids", []))
            stats = {
                "collection_name": self.collection.name,
                "document_count": total_docs,
                "persist_directory": self.persist_directory
            }
            logger.info(f"📊 Collection stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"🚨 Error fetching collection stats: {e}")
            return {"error": str(e)}
