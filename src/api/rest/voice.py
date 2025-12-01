"""
Voice-First REST API
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional, Dict, Any

from src.voice import VoiceCapture, WhisperClient, VoiceCommandProcessor
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VoiceTranscribeRequest(BaseModel):
    """Voice transcription request"""
    audio_file: Optional[str] = None
    language: str = "de"


class VoiceCommandRequest(BaseModel):
    """Voice command request"""
    command: str
    language: str = "de"


class VoiceAPI:
    """Voice-First API"""
    
    def __init__(self):
        self.router = APIRouter()
        self.whisper_client = WhisperClient()
        self.command_processor = VoiceCommandProcessor()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes"""
        @self.router.post("/transcribe")
        async def transcribe_audio(request: VoiceTranscribeRequest):
            """Transcribe audio file"""
            try:
                if not request.audio_file:
                    raise HTTPException(status_code=400, detail="audio_file required")
                
                transcription = self.whisper_client.transcribe(
                    audio_file=request.audio_file,
                    language=request.language,
                )
                
                return {"transcription": transcription}
            except Exception as e:
                logger.error(f"Error transcribing audio: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/transcribe/upload")
        async def transcribe_upload(audio: UploadFile = File(...), language: str = "de"):
            """Transcribe uploaded audio file"""
            try:
                # Save uploaded file temporarily
                from pathlib import Path
                import tempfile
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_path = tmp_file.name
                    tmp_file.write(await audio.read())
                
                transcription = self.whisper_client.transcribe(
                    audio_file=tmp_path,
                    language=language,
                )
                
                # Cleanup
                Path(tmp_path).unlink()
                
                return {"transcription": transcription}
            except Exception as e:
                logger.error(f"Error transcribing uploaded audio: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/command")
        async def process_command(request: VoiceCommandRequest):
            """Process voice command"""
            try:
                result = self.command_processor.process(
                    command=request.command,
                    language=request.language,
                )
                
                return {"result": result}
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                raise HTTPException(status_code=500, detail=str(e))

