"""
Merkle Tree for Batch Commits
"""

from typing import List
import hashlib

from src.utils.logger import get_logger

logger = get_logger(__name__)


class MerkleTree:
    """Merkle Tree"""
    
    def create_tree(self, hashes: List[str]) -> str:
        """Create Merkle tree from hashes"""
        if not hashes:
            return ""
        
        if len(hashes) == 1:
            return hashes[0]
        
        # Pair hashes and hash them together
        next_level = []
        for i in range(0, len(hashes), 2):
            if i + 1 < len(hashes):
                combined = hashes[i] + hashes[i + 1]
            else:
                combined = hashes[i] + hashes[i]  # Duplicate if odd
            
            next_hash = hashlib.sha256(combined.encode()).hexdigest()
            next_level.append(next_hash)
        
        # Recursively build tree
        return self.create_tree(next_level)
    
    def verify_proof(self, hash_value: str, merkle_root: str, proof: List[str]) -> bool:
        """Verify Merkle proof"""
        current_hash = hash_value
        
        for sibling in proof:
            combined = current_hash + sibling
            current_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        return current_hash == merkle_root

