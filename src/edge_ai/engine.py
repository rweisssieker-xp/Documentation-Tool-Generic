"""
Edge AI Engine - Zentrale Edge AI Engine
"""

from typing import Optional, Dict, Any
from enum import Enum

from .llm.llama import LlamaLLM
from .llm.mistral import MistralLLM
from .whisper.local_whisper import LocalWhisper
from .embeddings.local_embeddings import LocalEmbeddings
from .models.manager import ModelManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ModelType(Enum):
    """Model types"""
    LLAMA = "llama"
    MISTRAL = "mistral"
    PHI = "phi"


class EdgeAIEngine:
    """Edge AI Engine"""
    
    def __init__(
        self,
        model_type: ModelType = ModelType.LLAMA,
        model_path: Optional[str] = None,
        use_gpu: bool = True,
    ):
        """
        Initialize Edge AI Engine.
        
        Args:
            model_type: Model type to use
            model_path: Path to model file
            use_gpu: Use GPU acceleration
        """
        self.model_type = model_type
        self.model_path = model_path
        self.use_gpu = use_gpu
        
        self.model_manager = ModelManager()
        self.llm = None
        self.whisper = None
        self.embeddings = None
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize AI models"""
        try:
            # Initialize LLM
            if self.model_type == ModelType.LLAMA:
                self.llm = LlamaLLM(model_path=self.model_path, use_gpu=self.use_gpu)
            elif self.model_type == ModelType.MISTRAL:
                self.llm = MistralLLM(model_path=self.model_path, use_gpu=self.use_gpu)
            
            # Initialize Whisper
            self.whisper = LocalWhisper(use_gpu=self.use_gpu)
            
            # Initialize Embeddings
            self.embeddings = LocalEmbeddings()
            
            logger.info("Edge AI Engine initialized")
        except Exception as e:
            logger.error(f"Error initializing Edge AI Engine: {e}")
            # Fallback to cloud if available
            logger.warning("Falling back to cloud AI")
    
    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using local LLM"""
        if self.llm:
            return self.llm.generate(prompt, max_tokens=max_tokens)
        else:
            raise RuntimeError("LLM not initialized")
    
    def transcribe_audio(self, audio_file: str, language: str = "de") -> str:
        """Transcribe audio using local Whisper"""
        if self.whisper:
            return self.whisper.transcribe(audio_file, language=language)
        else:
            raise RuntimeError("Whisper not initialized")
    
    def generate_embeddings(self, text: str) -> list:
        """Generate embeddings using local model"""
        if self.embeddings:
            return self.embeddings.embed(text)
        else:
            raise RuntimeError("Embeddings not initialized")
    
    def is_available(self) -> bool:
        """Check if Edge AI is available"""
        return self.llm is not None and self.whisper is not None and self.embeddings is not None

