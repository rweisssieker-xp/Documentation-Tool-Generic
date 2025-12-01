"""
Local Whisper Integration
"""

from typing import Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


class LocalWhisper:
    """Local Whisper Integration"""
    
    def __init__(self, model_size: str = "base", use_gpu: bool = True):
        """
        Initialize Local Whisper.
        
        Args:
            model_size: Model size (tiny, base, small, medium, large)
            use_gpu: Use GPU acceleration
        """
        self.model_size = model_size
        self.use_gpu = use_gpu
        self.model = None
        
        try:
            import whisper
            self.whisper_available = True
            
            self.model = whisper.load_model(model_size, device="cuda" if use_gpu else "cpu")
            logger.info(f"Whisper model loaded: {model_size}")
        except ImportError:
            logger.warning("openai-whisper not available. Install with: pip install openai-whisper")
            self.whisper_available = False
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            self.whisper_available = False
    
    def transcribe(self, audio_file: str, language: str = "de") -> str:
        """Transcribe audio file"""
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            result = self.model.transcribe(audio_file, language=language)
            return result["text"]
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise

