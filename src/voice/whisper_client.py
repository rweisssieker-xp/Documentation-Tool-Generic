"""
Whisper Client - Transcribes audio using OpenAI Whisper API.
Part of Feature 7: Voice-First Documentation
"""

import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TranscriptionResult:
    """Result of audio transcription."""
    text: str
    language: str
    duration: float
    segments: List[Dict[str, Any]]
    timestamp: datetime
    audio_file: str
    confidence: float = 1.0


class WhisperClient:
    """
    Client for OpenAI Whisper API transcription.
    Supports real-time transcription of audio chunks.
    """
    
    SUPPORTED_FORMATS = ['.wav', '.mp3', '.m4a', '.webm', '.mp4', '.mpga', '.mpeg']
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "whisper-1",
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ):
        """
        Initialize Whisper client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Whisper model to use
            language: Target language code (e.g., 'de', 'en')
            prompt: Optional prompt to guide transcription
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai is required for Whisper. Install with: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.language = language
        self.prompt = prompt or "Documentation session. Technical terms and software UI elements."
        
        # Cache for recent transcriptions
        self._cache: Dict[str, TranscriptionResult] = {}
        
        logger.info(f"WhisperClient initialized with model: {model}")
    
    def transcribe_file(
        self,
        audio_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "verbose_json"
    ) -> TranscriptionResult:
        """
        Transcribe an audio file.
        
        Args:
            audio_path: Path to the audio file
            language: Override language for this transcription
            prompt: Override prompt for this transcription
            response_format: Response format (json, text, srt, verbose_json, vtt)
            
        Returns:
            TranscriptionResult with text and metadata
        """
        audio_path = Path(audio_path)
        
        # Validate file
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if audio_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {audio_path.suffix}")
        
        if audio_path.stat().st_size > self.MAX_FILE_SIZE:
            raise ValueError(f"File too large: {audio_path.stat().st_size} bytes (max {self.MAX_FILE_SIZE})")
        
        # Check cache
        cache_key = f"{audio_path}_{language or self.language}_{prompt or self.prompt}"
        if cache_key in self._cache:
            logger.debug(f"Returning cached transcription for: {audio_path}")
            return self._cache[cache_key]
        
        logger.info(f"Transcribing: {audio_path}")
        
        try:
            with open(audio_path, 'rb') as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language=language or self.language,
                    prompt=prompt or self.prompt,
                    response_format=response_format
                )
            
            # Parse response based on format
            if response_format == "verbose_json":
                result = TranscriptionResult(
                    text=response.text,
                    language=response.language if hasattr(response, 'language') else (language or self.language or 'unknown'),
                    duration=response.duration if hasattr(response, 'duration') else 0.0,
                    segments=response.segments if hasattr(response, 'segments') else [],
                    timestamp=datetime.now(),
                    audio_file=str(audio_path)
                )
            else:
                result = TranscriptionResult(
                    text=response if isinstance(response, str) else response.text,
                    language=language or self.language or 'unknown',
                    duration=0.0,
                    segments=[],
                    timestamp=datetime.now(),
                    audio_file=str(audio_path)
                )
            
            # Cache result
            self._cache[cache_key] = result
            
            logger.info(f"Transcription complete: {len(result.text)} chars, {result.duration:.1f}s")
            return result
        
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> TranscriptionResult:
        """
        Transcribe audio from bytes.
        
        Args:
            audio_bytes: Raw audio data
            filename: Filename hint for the API
            language: Override language
            prompt: Override prompt
            
        Returns:
            TranscriptionResult with text and metadata
        """
        import tempfile
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        try:
            result = self.transcribe_file(tmp_path, language, prompt)
            result.audio_file = filename  # Override with original filename
            return result
        finally:
            # Cleanup temp file
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    async def transcribe_async(
        self,
        audio_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> TranscriptionResult:
        """
        Async transcription for non-blocking operation.
        
        Args:
            audio_path: Path to audio file
            language: Override language
            prompt: Override prompt
            
        Returns:
            TranscriptionResult
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.transcribe_file(audio_path, language, prompt)
        )
    
    def translate_to_english(
        self,
        audio_path: str,
        prompt: Optional[str] = None
    ) -> TranscriptionResult:
        """
        Transcribe and translate audio to English.
        
        Args:
            audio_path: Path to audio file
            prompt: Override prompt
            
        Returns:
            TranscriptionResult with English text
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Translating to English: {audio_path}")
        
        try:
            with open(audio_path, 'rb') as audio_file:
                response = self.client.audio.translations.create(
                    model=self.model,
                    file=audio_file,
                    prompt=prompt or self.prompt,
                    response_format="verbose_json"
                )
            
            result = TranscriptionResult(
                text=response.text,
                language='en',
                duration=response.duration if hasattr(response, 'duration') else 0.0,
                segments=response.segments if hasattr(response, 'segments') else [],
                timestamp=datetime.now(),
                audio_file=str(audio_path)
            )
            
            logger.info(f"Translation complete: {len(result.text)} chars")
            return result
        
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise
    
    def clear_cache(self) -> None:
        """Clear transcription cache."""
        self._cache.clear()
        logger.debug("Transcription cache cleared")

