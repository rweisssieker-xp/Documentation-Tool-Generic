"""
Multi-Modal Capture REST API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from src.multimodal import MultiModalCaptureEngine
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CaptureStartRequest(BaseModel):
    """Capture start request"""
    output_dir: str


class CaptureStopResponse(BaseModel):
    """Capture stop response"""
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    mouse_data: Optional[Dict[str, Any]] = None
    keyboard_data: Optional[Dict[str, Any]] = None


class MultiModalAPI:
    """Multi-Modal Capture API"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        self.engine = MultiModalCaptureEngine()
    
    def _setup_routes(self):
        """Setup routes"""
        @self.router.post("/start")
        async def start_capture(request: CaptureStartRequest):
            """Start multi-modal capture"""
            try:
                if self.engine.is_recording():
                    raise HTTPException(status_code=400, detail="Capture already in progress")
                
                self.engine.start_recording(request.output_dir)
                return {"status": "started", "output_dir": request.output_dir}
            except Exception as e:
                logger.error(f"Error starting capture: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/stop", response_model=CaptureStopResponse)
        async def stop_capture():
            """Stop multi-modal capture"""
            try:
                if not self.engine.is_recording():
                    raise HTTPException(status_code=400, detail="No capture in progress")
                
                result = self.engine.stop_recording()
                return CaptureStopResponse(
                    video_path=result.get('video'),
                    audio_path=result.get('audio'),
                    mouse_data=result.get('mouse'),
                    keyboard_data=result.get('keyboard'),
                )
            except Exception as e:
                logger.error(f"Error stopping capture: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/status")
        async def get_status():
            """Get capture status"""
            return {"recording": self.engine.is_recording()}
