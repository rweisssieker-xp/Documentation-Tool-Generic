"""
Tests for Edge AI Engine
"""

import pytest

from src.edge_ai import EdgeAIEngine, ModelType


class TestEdgeAIEngine:
    """Test Edge AI Engine"""
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = EdgeAIEngine(model_type=ModelType.LLAMA)
        assert engine.model_type == ModelType.LLAMA
    
    def test_engine_is_available(self):
        """Test engine availability check"""
        engine = EdgeAIEngine(model_type=ModelType.LLAMA)
        # May be False if models not installed
        assert isinstance(engine.is_available(), bool)
    
    def test_create_document_hash(self):
        """Test document hash creation"""
        from src.blockchain import BlockchainAuditTrail
        
        blockchain = BlockchainAuditTrail()
        content = b"Test document content"
        doc_hash = blockchain.create_document_hash(content)
        
        assert isinstance(doc_hash, str)
        assert len(doc_hash) == 64  # SHA-256 hex length

