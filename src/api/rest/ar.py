"""
AR Documentation REST API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from src.ar import AROverlayEngine, ARPlatform
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AROverlayRequest(BaseModel):
    """AR overlay request"""
    content: str
    position: List[float]  # [x, y, z]
    anchor_id: Optional[str] = None
    platform: str = "vision_pro"


class AROverlayResponse(BaseModel):
    """AR overlay response"""
    anchor_id: str
    status: str


class ARAPI:
    """AR Documentation API"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        self.engines: Dict[str, AROverlayEngine] = {}
    
    def _setup_routes(self):
        """Setup routes"""
        @self.router.post("/overlay", response_model=AROverlayResponse)
        async def show_overlay(request: AROverlayRequest):
            """Show AR overlay"""
            try:
                platform_enum = ARPlatform.VISION_PRO if request.platform == "vision_pro" else ARPlatform.QUEST
                
                if request.platform not in self.engines:
                    self.engines[request.platform] = AROverlayEngine(platform=platform_enum)
                
                engine = self.engines[request.platform]
                anchor_id = request.anchor_id or f"anchor_{hash(request.content)}"
                
                engine.show_overlay(
                    request.content,
                    tuple(request.position),
                    anchor_id
                )
                
                return AROverlayResponse(anchor_id=anchor_id, status="shown")
            except Exception as e:
                logger.error(f"Error showing overlay: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.delete("/overlay/{anchor_id}")
        async def hide_overlay(anchor_id: str, platform: str = "vision_pro"):
            """Hide AR overlay"""
            try:
                if platform not in self.engines:
                    raise HTTPException(status_code=404, detail="Platform not initialized")
                
                engine = self.engines[platform]
                engine.hide_overlay(anchor_id)
                return {"status": "hidden"}
            except Exception as e:
                logger.error(f"Error hiding overlay: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.put("/overlay/{anchor_id}")
        async def update_overlay(anchor_id: str, content: str, platform: str = "vision_pro"):
            """Update AR overlay"""
            try:
                if platform not in self.engines:
                    raise HTTPException(status_code=404, detail="Platform not initialized")
                
                engine = self.engines[platform]
                engine.update_overlay(anchor_id, content)
                return {"status": "updated"}
            except Exception as e:
                logger.error(f"Error updating overlay: {e}")
                raise HTTPException(status_code=500, detail=str(e))
