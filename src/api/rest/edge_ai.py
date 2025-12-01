"""
Edge AI REST API
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional, Dict, Any
from src.edge_ai import EdgeAIEngine, ModelType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EdgeAIGenerateRequest(BaseModel):
    """Edge AI generation request"""
    prompt: str
    max_tokens: int = 500
    model_type: str = "llama"


class EdgeAITranscribeRequest(BaseModel):
    """Edge AI transcription request"""
    language: str = "de"


class EdgeAIResponse(BaseModel):
    """Edge AI response"""
    result: str
    model_used: str
    tokens_generated: Optional[int] = None


class EdgeAIAPI:
    """Edge AI API"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        self.engine: Optional[EdgeAIEngine] = None
    
    def _setup_routes(self):
        """Setup routes"""
        @self.router.post("/generate", response_model=EdgeAIResponse)
        async def generate_text(request: EdgeAIGenerateRequest):
            """Generate text using Edge AI"""
            try:
                if not self.engine:
                    if request.model_type == "llama":
                        model_type = ModelType.LLAMA
                    elif request.model_type == "mistral":
                        model_type = ModelType.MISTRAL
                    elif request.model_type == "phi":
                        model_type = ModelType.PHI
                    else:
                        model_type = ModelType.LLAMA
                    self.engine = EdgeAIEngine(model_type=model_type)
                
                if not self.engine.is_available():
                    raise HTTPException(status_code=503, detail="Edge AI not available")
                
                result = self.engine.generate_text(request.prompt, request.max_tokens)
                return EdgeAIResponse(
                    result=result,
                    model_used=request.model_type,
                    tokens_generated=len(result.split())
                )
            except Exception as e:
                logger.error(f"Error generating text: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/transcribe", response_model=EdgeAIResponse)
        async def transcribe_audio(
            audio: UploadFile = File(...),
            language: str = "de"
        ):
            """Transcribe audio using Edge AI"""
            try:
                if not self.engine:
                    self.engine = EdgeAIEngine()
                
                if not self.engine.is_available():
                    raise HTTPException(status_code=503, detail="Edge AI not available")
                
                # Save uploaded file temporarily
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    content = await audio.read()
                    tmp.write(content)
                    tmp_path = tmp.name
                
                result = self.engine.transcribe_audio(tmp_path, language)
                
                # Cleanup
                import os
                os.unlink(tmp_path)
                
                return EdgeAIResponse(
                    result=result,
                    model_used="whisper",
                )
            except Exception as e:
                logger.error(f"Error transcribing audio: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/status")
        async def get_status():
            """Get Edge AI status"""
            if not self.engine:
                return {"available": False, "reason": "Not initialized"}
            return {
                "available": self.engine.is_available(),
                "model_type": self.engine.model_type.value if self.engine.model_type else None,
            }
