"""
Local Embeddings Integration
"""

from typing import List

from src.utils.logger import get_logger

logger = get_logger(__name__)


class LocalEmbeddings:
    """Local Embeddings Integration"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize Local Embeddings.
        
        Args:
            model_name: Sentence transformer model name
        """
        self.model_name = model_name
        self.model = None
        
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            logger.info(f"Embeddings model loaded: {model_name}")
        except ImportError:
            logger.warning("sentence-transformers not available. Install with: pip install sentence-transformers")
        except Exception as e:
            logger.error(f"Error loading embeddings model: {e}")
    
    def embed(self, text: str) -> List[float]:
        """Generate embeddings"""
        if not self.model:
            raise RuntimeError("Embeddings model not loaded")
        
        try:
            embeddings = self.model.encode(text)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch"""
        if not self.model:
            raise RuntimeError("Embeddings model not loaded")
        
        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

