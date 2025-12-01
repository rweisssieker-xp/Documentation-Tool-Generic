"""
Blockchain Audit Trail REST API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from src.blockchain import BlockchainAuditTrail, BlockchainType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BlockchainStoreRequest(BaseModel):
    """Blockchain store request"""
    document_content: bytes
    metadata: Optional[Dict[str, Any]] = None
    blockchain_type: str = "polygon"


class BlockchainVerifyRequest(BaseModel):
    """Blockchain verify request"""
    document_content: bytes
    tx_hash: str


class BlockchainResponse(BaseModel):
    """Blockchain response"""
    tx_hash: str
    blockchain: str
    verified: Optional[bool] = None


class BlockchainAPI:
    """Blockchain Audit Trail API"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        self.trails: Dict[str, BlockchainAuditTrail] = {}
    
    def _setup_routes(self):
        """Setup routes"""
        @self.router.post("/store", response_model=BlockchainResponse)
        async def store_hash(request: BlockchainStoreRequest):
            """Store document hash on blockchain"""
            try:
                blockchain_type = BlockchainType.POLYGON if request.blockchain_type == "polygon" else BlockchainType.ETHEREUM
                
                if request.blockchain_type not in self.trails:
                    self.trails[request.blockchain_type] = BlockchainAuditTrail(blockchain_type=blockchain_type)
                
                trail = self.trails[request.blockchain_type]
                document_hash = trail.create_document_hash(request.document_content)
                tx_hash = trail.store_hash(document_hash, request.metadata)
                
                return BlockchainResponse(
                    tx_hash=tx_hash,
                    blockchain=request.blockchain_type,
                )
            except Exception as e:
                logger.error(f"Error storing hash: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/verify", response_model=BlockchainResponse)
        async def verify_hash(request: BlockchainVerifyRequest):
            """Verify document hash on blockchain"""
            try:
                # Try all blockchain types
                for blockchain_type in ["polygon", "ethereum"]:
                    if blockchain_type not in self.trails:
                        continue
                    
                    trail = self.trails[blockchain_type]
                    document_hash = trail.create_document_hash(request.document_content)
                    verified = trail.verify_hash(document_hash, request.tx_hash)
                    
                    if verified:
                        return BlockchainResponse(
                            tx_hash=request.tx_hash,
                            blockchain=blockchain_type,
                            verified=True,
                        )
                
                return BlockchainResponse(
                    tx_hash=request.tx_hash,
                    blockchain="unknown",
                    verified=False,
                )
            except Exception as e:
                logger.error(f"Error verifying hash: {e}")
                raise HTTPException(status_code=500, detail=str(e))
