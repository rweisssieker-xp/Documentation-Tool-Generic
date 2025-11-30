"""
Embedding Engine - Generates and manages embeddings for semantic search.
Part of Feature 4: Multi-Modal Knowledge Base
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import hashlib
import uuid

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Try to import optional dependencies
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class EmbeddingEngine:
    """
    Generates embeddings using OpenAI API and stores them in ChromaDB.
    Supports multi-modal content (text, image descriptions).
    """
    
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS = 1536
    
    def __init__(
        self,
        storage_dir: str = "data/embeddings",
        collection_name: str = "ahg_knowledge",
        api_key: Optional[str] = None
    ):
        """
        Initialize embedding engine.
        
        Args:
            storage_dir: Directory for ChromaDB storage
            collection_name: Name of the ChromaDB collection
            api_key: OpenAI API key (defaults to env var)
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb is required. Install with: pip install chromadb")
        
        if not OPENAI_AVAILABLE:
            raise ImportError("openai is required. Install with: pip install openai")
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.openai_client = OpenAI(api_key=self.api_key)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=str(self.storage_dir),
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Cache for embeddings
        self._cache: Dict[str, List[float]] = {}
        
        logger.info(f"EmbeddingEngine initialized: {collection_name}")
    
    def get_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Get embedding for text.
        
        Args:
            text: Text to embed
            use_cache: Whether to use cached embeddings
            
        Returns:
            Embedding vector
        """
        # Check cache
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        # Truncate text if too long (8191 tokens max)
        max_chars = 30000  # Approximate
        if len(text) > max_chars:
            text = text[:max_chars]
            logger.warning("Text truncated for embedding")
        
        try:
            response = self.openai_client.embeddings.create(
                model=self.EMBEDDING_MODEL,
                input=text
            )
            embedding = response.data[0].embedding
            
            # Cache result
            self._cache[cache_key] = embedding
            
            return embedding
        
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    def add_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add text to the embedding store.
        
        Args:
            text: Text to add
            metadata: Associated metadata
            doc_id: Custom document ID (generated if not provided)
            
        Returns:
            Document ID
        """
        doc_id = doc_id or str(uuid.uuid4())
        embedding = self.get_embedding(text)
        
        # Prepare metadata
        meta = metadata or {}
        meta["text_preview"] = text[:500] if len(text) > 500 else text
        
        # Add to collection
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[meta],
            documents=[text]
        )
        
        logger.debug(f"Added embedding: {doc_id}")
        return doc_id
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        doc_ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add multiple texts to the embedding store.
        
        Args:
            texts: List of texts
            metadatas: List of metadata dicts
            doc_ids: List of document IDs
            
        Returns:
            List of document IDs
        """
        if not texts:
            return []
        
        doc_ids = doc_ids or [str(uuid.uuid4()) for _ in texts]
        metadatas = metadatas or [{} for _ in texts]
        
        # Generate embeddings in batches
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = self.openai_client.embeddings.create(
                    model=self.EMBEDDING_MODEL,
                    input=batch
                )
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Batch embedding failed: {e}")
                # Fall back to individual embedding
                for text in batch:
                    try:
                        all_embeddings.append(self.get_embedding(text))
                    except:
                        all_embeddings.append([0.0] * self.EMBEDDING_DIMENSIONS)
        
        # Prepare metadatas
        for i, meta in enumerate(metadatas):
            meta["text_preview"] = texts[i][:500] if len(texts[i]) > 500 else texts[i]
        
        # Add to collection
        self.collection.add(
            ids=doc_ids,
            embeddings=all_embeddings,
            metadatas=metadatas,
            documents=texts
        )
        
        logger.info(f"Added {len(texts)} embeddings")
        return doc_ids
    
    def search(
        self,
        query: str,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            limit: Maximum number of results
            filter_metadata: Metadata filter
            
        Returns:
            List of search results with score and metadata
        """
        query_embedding = self.get_embedding(query)
        
        # Build where clause
        where = None
        if filter_metadata:
            where = filter_metadata
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                # Convert distance to similarity score (cosine)
                distance = results["distances"][0][i] if results["distances"] else 0
                score = 1 - distance  # Convert to similarity
                
                formatted.append({
                    "id": doc_id,
                    "score": score,
                    "document": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                })
        
        logger.debug(f"Search for '{query}': {len(formatted)} results")
        return formatted
    
    def delete(self, doc_id: str) -> bool:
        """
        Delete a document from the store.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if deleted
        """
        try:
            self.collection.delete(ids=[doc_id])
            logger.debug(f"Deleted embedding: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False
    
    def delete_by_metadata(self, filter_metadata: Dict[str, Any]) -> int:
        """
        Delete documents matching metadata filter.
        
        Args:
            filter_metadata: Metadata filter
            
        Returns:
            Number of deleted documents
        """
        # First, find matching IDs
        results = self.collection.get(
            where=filter_metadata,
            include=[]
        )
        
        if not results["ids"]:
            return 0
        
        # Delete
        self.collection.delete(ids=results["ids"])
        
        logger.info(f"Deleted {len(results['ids'])} embeddings by metadata")
        return len(results["ids"])
    
    def get_count(self) -> int:
        """Get total number of embeddings."""
        return self.collection.count()
    
    def clear(self) -> None:
        """Clear all embeddings."""
        # Delete and recreate collection
        collection_name = self.collection.name
        self.chroma_client.delete_collection(collection_name)
        self.collection = self.chroma_client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self._cache.clear()
        logger.info("Cleared all embeddings")
    
    def persist(self) -> None:
        """Persist embeddings to disk."""
        self.chroma_client.persist()
        logger.info("Embeddings persisted to disk")

