"""
Knowledge Base - Central storage for documentation with semantic search.
Part of Feature 4: Multi-Modal Knowledge Base
"""

import json
import hashlib
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import uuid

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class KnowledgeDocument:
    """A document stored in the knowledge base."""
    id: str
    title: str
    content: str
    doc_type: str  # session, step, annotation, manual
    source_file: Optional[str] = None
    session_id: Optional[str] = None
    step_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    embedding_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "doc_type": self.doc_type,
            "source_file": self.source_file,
            "session_id": self.session_id,
            "step_id": self.step_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "tags": self.tags,
            "embedding_id": self.embedding_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeDocument':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            content=data["content"],
            doc_type=data["doc_type"],
            source_file=data.get("source_file"),
            session_id=data.get("session_id"),
            step_id=data.get("step_id"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            embedding_id=data.get("embedding_id")
        )


@dataclass
class SearchResult:
    """A search result from the knowledge base."""
    document: KnowledgeDocument
    score: float
    highlights: List[str] = field(default_factory=list)


class KnowledgeBase:
    """
    Central knowledge base for all documentation.
    Supports semantic search and automatic categorization.
    """
    
    def __init__(
        self,
        storage_dir: str = "data/knowledge_base",
        embedding_engine: Optional[Any] = None
    ):
        """
        Initialize knowledge base.
        
        Args:
            storage_dir: Directory for storing knowledge base data
            embedding_engine: EmbeddingEngine instance for semantic search
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.embedding_engine = embedding_engine
        self._documents: Dict[str, KnowledgeDocument] = {}
        self._index: Dict[str, List[str]] = {
            "by_type": {},
            "by_session": {},
            "by_tag": {}
        }
        
        # Load existing documents
        self._load_documents()
        
        logger.info(f"KnowledgeBase initialized with {len(self._documents)} documents")
    
    def add_document(
        self,
        title: str,
        content: str,
        doc_type: str,
        source_file: Optional[str] = None,
        session_id: Optional[str] = None,
        step_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> KnowledgeDocument:
        """
        Add a document to the knowledge base.
        
        Args:
            title: Document title
            content: Document content
            doc_type: Type of document
            source_file: Source file path
            session_id: Related session ID
            step_id: Related step ID
            metadata: Additional metadata
            tags: Document tags
            
        Returns:
            Created KnowledgeDocument
        """
        doc_id = str(uuid.uuid4())
        
        doc = KnowledgeDocument(
            id=doc_id,
            title=title,
            content=content,
            doc_type=doc_type,
            source_file=source_file,
            session_id=session_id,
            step_id=step_id,
            metadata=metadata or {},
            tags=tags or []
        )
        
        # Generate embedding if engine available
        if self.embedding_engine:
            try:
                embedding_id = self.embedding_engine.add_text(
                    text=f"{title}\n\n{content}",
                    metadata={
                        "doc_id": doc_id,
                        "doc_type": doc_type,
                        "title": title
                    }
                )
                doc.embedding_id = embedding_id
            except Exception as e:
                logger.warning(f"Failed to create embedding: {e}")
        
        # Store document
        self._documents[doc_id] = doc
        
        # Update indices
        self._update_index(doc)
        
        # Save to disk
        self._save_document(doc)
        
        logger.info(f"Added document: {doc_id} - {title}")
        return doc
    
    def add_session(
        self,
        session_data: Dict[str, Any],
        include_steps: bool = True
    ) -> List[KnowledgeDocument]:
        """
        Add a complete session to the knowledge base.
        
        Args:
            session_data: Session data dictionary
            include_steps: Whether to add individual steps as documents
            
        Returns:
            List of created documents
        """
        documents = []
        session_id = session_data.get("session_id", str(uuid.uuid4()))
        
        # Add session overview document
        session_content = self._format_session_overview(session_data)
        session_doc = self.add_document(
            title=f"Session: {session_data.get('name', session_id)}",
            content=session_content,
            doc_type="session",
            session_id=session_id,
            metadata={
                "step_count": len(session_data.get("steps", [])),
                "created": session_data.get("created"),
                "application": session_data.get("application")
            },
            tags=["session", session_data.get("application", "unknown")]
        )
        documents.append(session_doc)
        
        # Add individual steps
        if include_steps:
            for i, step in enumerate(session_data.get("steps", [])):
                step_content = self._format_step_content(step)
                step_doc = self.add_document(
                    title=f"Step {i+1}: {step.get('title', 'Untitled')}",
                    content=step_content,
                    doc_type="step",
                    session_id=session_id,
                    step_id=step.get("id", f"step_{i}"),
                    metadata={
                        "step_number": i + 1,
                        "screenshot": step.get("screenshot"),
                        "window_title": step.get("window_title")
                    },
                    tags=["step", session_data.get("application", "unknown")]
                )
                documents.append(step_doc)
        
        logger.info(f"Added session {session_id} with {len(documents)} documents")
        return documents
    
    def get_document(self, doc_id: str) -> Optional[KnowledgeDocument]:
        """Get document by ID."""
        return self._documents.get(doc_id)
    
    def get_documents_by_type(self, doc_type: str) -> List[KnowledgeDocument]:
        """Get all documents of a specific type."""
        doc_ids = self._index["by_type"].get(doc_type, [])
        return [self._documents[did] for did in doc_ids if did in self._documents]
    
    def get_documents_by_session(self, session_id: str) -> List[KnowledgeDocument]:
        """Get all documents for a session."""
        doc_ids = self._index["by_session"].get(session_id, [])
        return [self._documents[did] for did in doc_ids if did in self._documents]
    
    def get_documents_by_tag(self, tag: str) -> List[KnowledgeDocument]:
        """Get all documents with a specific tag."""
        doc_ids = self._index["by_tag"].get(tag, [])
        return [self._documents[did] for did in doc_ids if did in self._documents]
    
    def search(
        self,
        query: str,
        doc_type: Optional[str] = None,
        limit: int = 10,
        semantic: bool = True
    ) -> List[SearchResult]:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            doc_type: Filter by document type
            limit: Maximum number of results
            semantic: Use semantic search if available
            
        Returns:
            List of SearchResult objects
        """
        results = []
        
        # Use semantic search if available
        if semantic and self.embedding_engine:
            try:
                semantic_results = self.embedding_engine.search(
                    query=query,
                    limit=limit * 2,  # Get more for filtering
                    filter_metadata={"doc_type": doc_type} if doc_type else None
                )
                
                for sr in semantic_results:
                    doc_id = sr.get("metadata", {}).get("doc_id")
                    if doc_id and doc_id in self._documents:
                        doc = self._documents[doc_id]
                        if doc_type is None or doc.doc_type == doc_type:
                            results.append(SearchResult(
                                document=doc,
                                score=sr.get("score", 0.0),
                                highlights=self._extract_highlights(doc.content, query)
                            ))
                            
                            if len(results) >= limit:
                                break
                
                logger.info(f"Semantic search for '{query}': {len(results)} results")
                return results
            
            except Exception as e:
                logger.warning(f"Semantic search failed, falling back to keyword: {e}")
        
        # Fallback to keyword search
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for doc in self._documents.values():
            if doc_type and doc.doc_type != doc_type:
                continue
            
            # Simple relevance scoring
            content_lower = doc.content.lower()
            title_lower = doc.title.lower()
            
            score = 0.0
            if query_lower in title_lower:
                score += 2.0
            if query_lower in content_lower:
                score += 1.0
            
            word_matches = sum(1 for w in query_words if w in content_lower)
            score += word_matches * 0.3
            
            if score > 0:
                results.append(SearchResult(
                    document=doc,
                    score=score,
                    highlights=self._extract_highlights(doc.content, query)
                ))
        
        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)
        
        logger.info(f"Keyword search for '{query}': {len(results[:limit])} results")
        return results[:limit]
    
    def get_related_documents(
        self,
        doc_id: str,
        limit: int = 5
    ) -> List[SearchResult]:
        """
        Get documents related to a specific document.
        
        Args:
            doc_id: Document ID
            limit: Maximum number of results
            
        Returns:
            List of related documents
        """
        doc = self._documents.get(doc_id)
        if not doc:
            return []
        
        # Use document content as query
        return self.search(
            query=f"{doc.title} {doc.content[:500]}",
            doc_type=None,
            limit=limit + 1,
            semantic=True
        )[1:limit+1]  # Exclude the document itself
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the knowledge base.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if deleted successfully
        """
        if doc_id not in self._documents:
            return False
        
        doc = self._documents[doc_id]
        
        # Remove from embedding store
        if self.embedding_engine and doc.embedding_id:
            try:
                self.embedding_engine.delete(doc.embedding_id)
            except Exception as e:
                logger.warning(f"Failed to delete embedding: {e}")
        
        # Remove from indices
        self._remove_from_index(doc)
        
        # Remove document
        del self._documents[doc_id]
        
        # Delete file
        doc_file = self.storage_dir / "documents" / f"{doc_id}.json"
        if doc_file.exists():
            doc_file.unlink()
        
        logger.info(f"Deleted document: {doc_id}")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        type_counts = {}
        for doc in self._documents.values():
            type_counts[doc.doc_type] = type_counts.get(doc.doc_type, 0) + 1
        
        return {
            "total_documents": len(self._documents),
            "documents_by_type": type_counts,
            "total_sessions": len(self._index["by_session"]),
            "unique_tags": len(self._index["by_tag"]),
            "storage_dir": str(self.storage_dir)
        }
    
    def _format_session_overview(self, session_data: Dict[str, Any]) -> str:
        """Format session data as overview content."""
        lines = [
            f"# {session_data.get('name', 'Documentation Session')}",
            "",
            f"**Application:** {session_data.get('application', 'Unknown')}",
            f"**Created:** {session_data.get('created', 'Unknown')}",
            f"**Steps:** {len(session_data.get('steps', []))}",
            "",
            "## Steps Overview",
            ""
        ]
        
        for i, step in enumerate(session_data.get("steps", [])):
            lines.append(f"{i+1}. {step.get('title', step.get('description', 'Untitled'))}")
        
        return "\n".join(lines)
    
    def _format_step_content(self, step: Dict[str, Any]) -> str:
        """Format step data as document content."""
        lines = [
            step.get("title", "Untitled Step"),
            "",
            step.get("description", ""),
            "",
            f"**Window:** {step.get('window_title', 'Unknown')}",
            f"**Time:** {step.get('timestamp', 'Unknown')}"
        ]
        
        if step.get("ocr_text"):
            lines.extend([
                "",
                "## OCR Text",
                step["ocr_text"]
            ])
        
        return "\n".join(lines)
    
    def _extract_highlights(self, content: str, query: str, context_chars: int = 100) -> List[str]:
        """Extract highlighted snippets from content."""
        highlights = []
        query_lower = query.lower()
        content_lower = content.lower()
        
        start = 0
        while True:
            pos = content_lower.find(query_lower, start)
            if pos == -1:
                break
            
            # Extract context around match
            snippet_start = max(0, pos - context_chars)
            snippet_end = min(len(content), pos + len(query) + context_chars)
            snippet = content[snippet_start:snippet_end]
            
            if snippet_start > 0:
                snippet = "..." + snippet
            if snippet_end < len(content):
                snippet = snippet + "..."
            
            highlights.append(snippet)
            start = pos + 1
            
            if len(highlights) >= 3:
                break
        
        return highlights
    
    def _update_index(self, doc: KnowledgeDocument) -> None:
        """Update indices with document."""
        # By type
        if doc.doc_type not in self._index["by_type"]:
            self._index["by_type"][doc.doc_type] = []
        if doc.id not in self._index["by_type"][doc.doc_type]:
            self._index["by_type"][doc.doc_type].append(doc.id)
        
        # By session
        if doc.session_id:
            if doc.session_id not in self._index["by_session"]:
                self._index["by_session"][doc.session_id] = []
            if doc.id not in self._index["by_session"][doc.session_id]:
                self._index["by_session"][doc.session_id].append(doc.id)
        
        # By tag
        for tag in doc.tags:
            if tag not in self._index["by_tag"]:
                self._index["by_tag"][tag] = []
            if doc.id not in self._index["by_tag"][tag]:
                self._index["by_tag"][tag].append(doc.id)
    
    def _remove_from_index(self, doc: KnowledgeDocument) -> None:
        """Remove document from indices."""
        if doc.doc_type in self._index["by_type"]:
            if doc.id in self._index["by_type"][doc.doc_type]:
                self._index["by_type"][doc.doc_type].remove(doc.id)
        
        if doc.session_id and doc.session_id in self._index["by_session"]:
            if doc.id in self._index["by_session"][doc.session_id]:
                self._index["by_session"][doc.session_id].remove(doc.id)
        
        for tag in doc.tags:
            if tag in self._index["by_tag"]:
                if doc.id in self._index["by_tag"][tag]:
                    self._index["by_tag"][tag].remove(doc.id)
    
    def _save_document(self, doc: KnowledgeDocument) -> None:
        """Save document to disk."""
        docs_dir = self.storage_dir / "documents"
        docs_dir.mkdir(exist_ok=True)
        
        filepath = docs_dir / f"{doc.id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(doc.to_dict(), f, indent=2, ensure_ascii=False)
    
    def _load_documents(self) -> None:
        """Load documents from disk."""
        docs_dir = self.storage_dir / "documents"
        if not docs_dir.exists():
            return
        
        for filepath in docs_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                doc = KnowledgeDocument.from_dict(data)
                self._documents[doc.id] = doc
                self._update_index(doc)
            except Exception as e:
                logger.error(f"Failed to load document {filepath}: {e}")
        
        logger.info(f"Loaded {len(self._documents)} documents from disk")
    
    def save_index(self) -> None:
        """Save index to disk."""
        index_file = self.storage_dir / "index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(self._index, f, indent=2)

