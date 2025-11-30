"""
Semantic Search - High-level search interface for the knowledge base.
Part of Feature 4: Multi-Modal Knowledge Base
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)


class SearchMode(Enum):
    """Search modes."""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"


@dataclass
class SemanticSearchResult:
    """A semantic search result."""
    id: str
    title: str
    content: str
    score: float
    doc_type: str
    highlights: List[str]
    metadata: Dict[str, Any]


class SemanticSearch:
    """
    High-level semantic search interface.
    Combines vector search with keyword matching for best results.
    """
    
    def __init__(
        self,
        knowledge_base: Any,
        embedding_engine: Any
    ):
        """
        Initialize semantic search.
        
        Args:
            knowledge_base: KnowledgeBase instance
            embedding_engine: EmbeddingEngine instance
        """
        self.kb = knowledge_base
        self.embeddings = embedding_engine
        
        logger.info("SemanticSearch initialized")
    
    def search(
        self,
        query: str,
        mode: SearchMode = SearchMode.HYBRID,
        doc_types: Optional[List[str]] = None,
        limit: int = 10,
        min_score: float = 0.3
    ) -> List[SemanticSearchResult]:
        """
        Perform semantic search.
        
        Args:
            query: Search query
            mode: Search mode (semantic, keyword, hybrid)
            doc_types: Filter by document types
            limit: Maximum number of results
            min_score: Minimum relevance score
            
        Returns:
            List of SemanticSearchResult objects
        """
        results = []
        
        if mode in [SearchMode.SEMANTIC, SearchMode.HYBRID]:
            # Vector search
            vector_results = self._vector_search(query, limit * 2, doc_types)
            results.extend(vector_results)
        
        if mode in [SearchMode.KEYWORD, SearchMode.HYBRID]:
            # Keyword search
            keyword_results = self._keyword_search(query, limit * 2, doc_types)
            
            # Merge results (avoid duplicates)
            existing_ids = {r.id for r in results}
            for kr in keyword_results:
                if kr.id not in existing_ids:
                    results.append(kr)
                else:
                    # Boost score for documents found by both methods
                    for r in results:
                        if r.id == kr.id:
                            r.score = min(1.0, r.score * 1.2)
                            break
        
        # Filter by minimum score
        results = [r for r in results if r.score >= min_score]
        
        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)
        
        logger.info(f"Search '{query}' ({mode.value}): {len(results[:limit])} results")
        return results[:limit]
    
    def find_similar(
        self,
        text: str,
        limit: int = 5,
        exclude_ids: Optional[List[str]] = None
    ) -> List[SemanticSearchResult]:
        """
        Find documents similar to given text.
        
        Args:
            text: Reference text
            limit: Maximum number of results
            exclude_ids: IDs to exclude from results
            
        Returns:
            List of similar documents
        """
        exclude_ids = set(exclude_ids or [])
        
        vector_results = self.embeddings.search(text, limit=limit + len(exclude_ids))
        
        results = []
        for vr in vector_results:
            if vr["id"] in exclude_ids:
                continue
            
            doc = self.kb.get_document(vr.get("metadata", {}).get("doc_id", ""))
            if doc:
                results.append(SemanticSearchResult(
                    id=doc.id,
                    title=doc.title,
                    content=doc.content[:500],
                    score=vr["score"],
                    doc_type=doc.doc_type,
                    highlights=[],
                    metadata=doc.metadata
                ))
            
            if len(results) >= limit:
                break
        
        return results
    
    def answer_question(
        self,
        question: str,
        context_limit: int = 5
    ) -> Dict[str, Any]:
        """
        Answer a question using the knowledge base.
        
        Args:
            question: Question to answer
            context_limit: Number of documents to use as context
            
        Returns:
            Answer with sources
        """
        # Find relevant documents
        results = self.search(
            query=question,
            mode=SearchMode.HYBRID,
            limit=context_limit
        )
        
        if not results:
            return {
                "answer": "Keine relevanten Informationen gefunden.",
                "confidence": 0.0,
                "sources": []
            }
        
        # Build context from results
        context_parts = []
        sources = []
        
        for r in results:
            context_parts.append(f"[{r.title}]\n{r.content}")
            sources.append({
                "id": r.id,
                "title": r.title,
                "score": r.score,
                "doc_type": r.doc_type
            })
        
        context = "\n\n---\n\n".join(context_parts)
        
        return {
            "context": context,
            "sources": sources,
            "confidence": results[0].score if results else 0.0,
            "query": question
        }
    
    def _vector_search(
        self,
        query: str,
        limit: int,
        doc_types: Optional[List[str]] = None
    ) -> List[SemanticSearchResult]:
        """Perform vector similarity search."""
        results = []
        
        try:
            # Build filter
            filter_meta = None
            if doc_types:
                filter_meta = {"doc_type": {"$in": doc_types}}
            
            vector_results = self.embeddings.search(
                query=query,
                limit=limit,
                filter_metadata=filter_meta
            )
            
            for vr in vector_results:
                doc_id = vr.get("metadata", {}).get("doc_id")
                if doc_id:
                    doc = self.kb.get_document(doc_id)
                    if doc:
                        results.append(SemanticSearchResult(
                            id=doc.id,
                            title=doc.title,
                            content=doc.content[:500],
                            score=vr["score"],
                            doc_type=doc.doc_type,
                            highlights=self._extract_highlights(doc.content, query),
                            metadata=doc.metadata
                        ))
        
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
        
        return results
    
    def _keyword_search(
        self,
        query: str,
        limit: int,
        doc_types: Optional[List[str]] = None
    ) -> List[SemanticSearchResult]:
        """Perform keyword-based search."""
        kb_results = self.kb.search(
            query=query,
            doc_type=doc_types[0] if doc_types and len(doc_types) == 1 else None,
            limit=limit,
            semantic=False
        )
        
        results = []
        for kr in kb_results:
            if doc_types and kr.document.doc_type not in doc_types:
                continue
            
            results.append(SemanticSearchResult(
                id=kr.document.id,
                title=kr.document.title,
                content=kr.document.content[:500],
                score=min(kr.score / 5.0, 1.0),  # Normalize score
                doc_type=kr.document.doc_type,
                highlights=kr.highlights,
                metadata=kr.document.metadata
            ))
        
        return results
    
    def _extract_highlights(self, content: str, query: str, context_chars: int = 100) -> List[str]:
        """Extract highlighted snippets from content."""
        highlights = []
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Find query words
        query_words = query_lower.split()
        
        for word in query_words:
            if len(word) < 3:
                continue
            
            pos = content_lower.find(word)
            if pos != -1:
                start = max(0, pos - context_chars)
                end = min(len(content), pos + len(word) + context_chars)
                snippet = content[start:end]
                
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."
                
                if snippet not in highlights:
                    highlights.append(snippet)
                
                if len(highlights) >= 3:
                    break
        
        return highlights

