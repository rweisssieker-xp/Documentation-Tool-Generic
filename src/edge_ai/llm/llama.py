"""
Llama LLM Integration
"""

from typing import Optional
import logging

from src.utils.logger import get_logger

logger = get_logger(__name__)


class LlamaLLM:
    """Llama LLM Integration"""
    
    def __init__(self, model_path: Optional[str] = None, use_gpu: bool = True):
        """
        Initialize Llama LLM.
        
        Args:
            model_path: Path to Llama model
            use_gpu: Use GPU acceleration
        """
        self.model_path = model_path
        self.use_gpu = use_gpu
        self.model = None
        
        try:
            # Try to import llama-cpp-python
            import llama_cpp
            self.llama_available = True
            
            if model_path:
                self.model = llama_cpp.Llama(
                    model_path=model_path,
                    n_gpu_layers=-1 if use_gpu else 0,
                )
            else:
                logger.warning("No model path provided for Llama")
        except ImportError:
            logger.warning("llama-cpp-python not available. Install with: pip install llama-cpp-python")
            self.llama_available = False
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text"""
        if not self.model:
            raise RuntimeError("Llama model not loaded")
        
        try:
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9,
            )
            return response['choices'][0]['text']
        except Exception as e:
            logger.error(f"Error generating text with Llama: {e}")
            raise

