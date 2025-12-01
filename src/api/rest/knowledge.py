"""
Knowledge Base REST API
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from src.knowledge import KnowledgeBase, SemanticSearch, RAGEngine
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentAddRequest(BaseModel):
    """Add document request"""
    content: str
    title: str
    doc_type: str = "manual"
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    """Search request"""
    query: str
    top_k: int = 5
    use_semantic: bool = True


class RAGQueryRequest(BaseModel):
    """RAG query request"""
    question: str
    context_documents: Optional[List[str]] = None


class KnowledgeAPI:
    """Knowledge Base API"""
    
    def __init__(self):
        self.router = APIRouter()
        self.knowledge_base = KnowledgeBase()
        self.semantic_search = SemanticSearch(self.knowledge_base)
        self.rag_engine = RAGEngine(self.knowledge_base)
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes"""
        @self.router.post("/documents")
        async def add_document(request: DocumentAddRequest):
            """Add document to knowledge base"""
            try:
                doc_id = self.knowledge_base.add_document(
                    content=request.content,
                    title=request.title,
                    doc_type=request.doc_type,
                    metadata=request.metadata or {},
                )
                return {"id": doc_id, "message": "Document added"}
            except Exception as e:
                logger.error(f"Error adding document: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/documents")
        async def list_documents():
            """List all documents"""
            try:
                documents = self.knowledge_base.list_documents()
                return {"documents": documents}
            except Exception as e:
                logger.error(f"Error listing documents: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/search")
        async def search(request: SearchRequest):
            """Search knowledge base"""
            try:
                if request.use_semantic:
                    results = self.semantic_search.search(request.query, top_k=request.top_k)
                else:
                    results = self.knowledge_base.search(request.query, limit=request.top_k)
                
                return {"results": results}
            except Exception as e:
                logger.error(f"Error searching: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/rag/query")
        async def rag_query(request: RAGQueryRequest):
            """Query RAG engine"""
            try:
                answer = self.rag_engine.query(
                    question=request.question,
                    context_documents=request.context_documents,
                )
                return {"answer": answer}
            except Exception as e:
                logger.error(f"Error querying RAG: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/stats")
        async def get_stats():
            """Get knowledge base statistics"""
            try:
                stats = self.knowledge_base.get_statistics()
                return stats
            except Exception as e:
                logger.error(f"Error getting stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))

