"""
Blockchain Audit Trail - Zentrale Blockchain-Integration
"""

from typing import Optional, Dict, Any, List
from enum import Enum
import hashlib

from .chains.ethereum import EthereumChain
from .chains.polygon import PolygonChain
from .hashing.merkle_tree import MerkleTree
from .verification.validator import DocumentValidator
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BlockchainType(Enum):
    """Blockchain types"""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    PRIVATE = "private"


class BlockchainAuditTrail:
    """Blockchain Audit Trail"""
    
    def __init__(
        self,
        blockchain_type: BlockchainType = BlockchainType.POLYGON,
        private_key: Optional[str] = None,
    ):
        """
        Initialize Blockchain Audit Trail.
        
        Args:
            blockchain_type: Blockchain to use
            private_key: Private key for signing (optional)
        """
        self.blockchain_type = blockchain_type
        self.private_key = private_key
        
        self.chain = None
        self.merkle_tree = MerkleTree()
        self.validator = DocumentValidator()
        
        self._initialize_chain()
    
    def _initialize_chain(self):
        """Initialize blockchain connection"""
        try:
            if self.blockchain_type == BlockchainType.ETHEREUM:
                self.chain = EthereumChain(private_key=self.private_key)
            elif self.blockchain_type == BlockchainType.POLYGON:
                self.chain = PolygonChain(private_key=self.private_key)
            else:
                logger.warning(f"Blockchain type {self.blockchain_type} not fully implemented")
        except Exception as e:
            logger.error(f"Error initializing blockchain: {e}")
    
    def store_hash(self, document_hash: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store document hash on blockchain"""
        if not self.chain:
            raise RuntimeError("Blockchain not initialized")
        
        try:
            # Create transaction
            tx_hash = self.chain.store_hash(document_hash, metadata)
            logger.info(f"Hash stored on blockchain: {tx_hash}")
            return tx_hash
        except Exception as e:
            logger.error(f"Error storing hash: {e}")
            raise
    
    def batch_store(self, hashes: List[str]) -> str:
        """Batch store multiple hashes using Merkle Tree"""
        merkle_root = self.merkle_tree.create_tree(hashes)
        tx_hash = self.store_hash(merkle_root, {"type": "merkle_root", "count": len(hashes)})
        return tx_hash
    
    def verify_hash(self, document_hash: str, tx_hash: str) -> bool:
        """Verify document hash on blockchain"""
        if not self.chain:
            raise RuntimeError("Blockchain not initialized")
        
        try:
            stored_hash = self.chain.get_hash(tx_hash)
            return stored_hash == document_hash
        except Exception as e:
            logger.error(f"Error verifying hash: {e}")
            return False
    
    def create_document_hash(self, document_content: bytes) -> str:
        """Create SHA-256 hash of document"""
        return hashlib.sha256(document_content).hexdigest()

