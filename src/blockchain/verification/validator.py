"""
Document Validator - Verifiziert Dokumente gegen Blockchain
"""

from typing import Optional
import hashlib

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentValidator:
    """Document Validator"""
    
    def validate_document(self, document_content: bytes, stored_hash: str) -> bool:
        """Validate document against stored hash"""
        current_hash = hashlib.sha256(document_content).hexdigest()
        return current_hash == stored_hash
    
    def create_hash(self, document_content: bytes) -> str:
        """Create hash of document"""
        return hashlib.sha256(document_content).hexdigest()

