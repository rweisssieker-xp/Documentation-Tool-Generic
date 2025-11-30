"""
Tests for Multi-Modal Knowledge Base Module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json


class TestKnowledgeBase:
    """Tests for KnowledgeBase class."""
    
    def test_knowledge_base_initialization(self, tmp_path):
        """Test KnowledgeBase initialization."""
        from src.knowledge.knowledge_base import KnowledgeBase
        
        kb = KnowledgeBase(storage_dir=str(tmp_path))
        
        assert kb.storage_dir.exists()
        assert len(kb._documents) == 0
    
    def test_add_document(self, tmp_path):
        """Test adding a document."""
        from src.knowledge.knowledge_base import KnowledgeBase
        
        kb = KnowledgeBase(storage_dir=str(tmp_path))
        
        doc = kb.add_document(
            title="Test Document",
            content="This is test content",
            doc_type="manual",
            tags=["test", "example"]
        )
        
        assert doc.title == "Test Document"
        assert doc.doc_type == "manual"
        assert "test" in doc.tags
    
    def test_get_document(self, tmp_path):
        """Test retrieving a document."""
        from src.knowledge.knowledge_base import KnowledgeBase
        
        kb = KnowledgeBase(storage_dir=str(tmp_path))
        
        doc = kb.add_document(
            title="Test",
            content="Content",
            doc_type="test"
        )
        
        retrieved = kb.get_document(doc.id)
        assert retrieved is not None
        assert retrieved.title == "Test"
    
    def test_search_keyword(self, tmp_path):
        """Test keyword search."""
        from src.knowledge.knowledge_base import KnowledgeBase
        
        kb = KnowledgeBase(storage_dir=str(tmp_path))
        
        kb.add_document(title="Python Guide", content="Learn Python programming", doc_type="guide")
        kb.add_document(title="Java Guide", content="Learn Java programming", doc_type="guide")
        
        results = kb.search("Python", semantic=False)
        
        assert len(results) >= 1
        assert any("Python" in r.document.title for r in results)
    
    def test_get_documents_by_type(self, tmp_path):
        """Test filtering documents by type."""
        from src.knowledge.knowledge_base import KnowledgeBase
        
        kb = KnowledgeBase(storage_dir=str(tmp_path))
        
        kb.add_document(title="Doc 1", content="Content 1", doc_type="session")
        kb.add_document(title="Doc 2", content="Content 2", doc_type="manual")
        kb.add_document(title="Doc 3", content="Content 3", doc_type="session")
        
        sessions = kb.get_documents_by_type("session")
        assert len(sessions) == 2
    
    def test_delete_document(self, tmp_path):
        """Test deleting a document."""
        from src.knowledge.knowledge_base import KnowledgeBase
        
        kb = KnowledgeBase(storage_dir=str(tmp_path))
        
        doc = kb.add_document(title="To Delete", content="Content", doc_type="test")
        
        result = kb.delete_document(doc.id)
        assert result == True
        assert kb.get_document(doc.id) is None
    
    def test_add_session(self, tmp_path):
        """Test adding a complete session."""
        from src.knowledge.knowledge_base import KnowledgeBase
        
        kb = KnowledgeBase(storage_dir=str(tmp_path))
        
        session_data = {
            "session_id": "sess_001",
            "name": "Test Session",
            "steps": [
                {"id": "step_1", "title": "Step 1", "description": "First step"},
                {"id": "step_2", "title": "Step 2", "description": "Second step"}
            ]
        }
        
        docs = kb.add_session(session_data, include_steps=True)
        
        assert len(docs) == 3  # 1 session + 2 steps
    
    def test_get_statistics(self, tmp_path):
        """Test getting statistics."""
        from src.knowledge.knowledge_base import KnowledgeBase
        
        kb = KnowledgeBase(storage_dir=str(tmp_path))
        
        kb.add_document(title="Doc 1", content="Content", doc_type="test")
        kb.add_document(title="Doc 2", content="Content", doc_type="test")
        
        stats = kb.get_statistics()
        assert stats["total_documents"] == 2


class TestSemanticSearch:
    """Tests for SemanticSearch class."""
    
    def test_search_mode_enum(self):
        """Test SearchMode enum."""
        from src.knowledge.semantic_search import SearchMode
        
        assert SearchMode.SEMANTIC.value == "semantic"
        assert SearchMode.KEYWORD.value == "keyword"
        assert SearchMode.HYBRID.value == "hybrid"


class TestRAGEngine:
    """Tests for RAGEngine class."""
    
    @patch('src.knowledge.rag_engine.OPENAI_AVAILABLE', True)
    @patch('src.knowledge.rag_engine.OpenAI')
    def test_rag_engine_initialization(self, mock_openai):
        """Test RAGEngine initialization."""
        from src.knowledge.rag_engine import RAGEngine
        
        mock_search = Mock()
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            rag = RAGEngine(semantic_search=mock_search, language='de')
            assert rag.language == 'de'

