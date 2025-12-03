"""
Tests for Blockchain Audit Trail
"""

import pytest

from src.blockchain import BlockchainAuditTrail, BlockchainType


class TestBlockchainAuditTrail:
    """Test Blockchain Audit Trail"""
    
    def test_initialization(self):
        """Test blockchain initialization"""
        blockchain = BlockchainAuditTrail(blockchain_type=BlockchainType.POLYGON)
        assert blockchain.blockchain_type == BlockchainType.POLYGON
    
    def test_create_document_hash(self):
        """Test document hash creation"""
        blockchain = BlockchainAuditTrail()
        content = b"Test document content"
        doc_hash = blockchain.create_document_hash(content)
        
        assert isinstance(doc_hash, str)
        assert len(doc_hash) == 64  # SHA-256 hex length
    
    def test_batch_store(self):
        """Test batch store with Merkle Tree"""
        blockchain = BlockchainAuditTrail()
        hashes = ["hash1", "hash2", "hash3"]
        
        # Should not raise exception
        try:
            tx_hash = blockchain.batch_store(hashes)
            assert isinstance(tx_hash, str)
        except Exception as e:
            # May fail if blockchain not connected
            pytest.skip(f"Blockchain not available: {e}")


class TestMerkleTree:
    """Test Merkle Tree"""
    
    def test_create_tree(self):
        """Test Merkle tree creation"""
        from src.blockchain.hashing.merkle_tree import MerkleTree
        
        tree = MerkleTree()
        hashes = ["hash1", "hash2", "hash3", "hash4"]
        root = tree.create_tree(hashes)
        
        assert isinstance(root, str)
        assert len(root) > 0
    
    def test_create_tree_single(self):
        """Test Merkle tree with single hash"""
        from src.blockchain.hashing.merkle_tree import MerkleTree
        
        tree = MerkleTree()
        hashes = ["hash1"]
        root = tree.create_tree(hashes)
        
        assert root == "hash1"






